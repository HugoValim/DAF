import os
import functools
from dataclasses import dataclass

from kafka import KafkaProducer
import msgpack

from apstools.callbacks import NXWriter
import apstools.utils as au

import databroker
from bluesky import RunEngine

from bluesky.plans import count, scan, rel_scan, list_scan, grid_scan
from ophyd import EpicsMotor, EpicsSignalRO
from lnls_ophyd.area_detectors.pilatus_300k import Pilatus, Pilatus6ROIs
from bluesky.callbacks.best_effort import BestEffortCallback
from bluesky.utils import ProgressBarManager

from daf.utils import dafutilities as du
from daf.utils.utils import create_unique_file_name
from .signal_handler import DAFSigIntHandler


@dataclass
class DAFScanInputs:
    scan_data: dict = None
    inputed_motors: tuple = ()
    motors_data_dict: dict = None
    counters: tuple = ()
    main_counter: str = None
    scan_type: str = None
    steps: int = None
    acquisition_time: float = None
    delay_time: float = None
    output: str = None
    kafka_topic: str = None
    scan_db: str = None


class DAFScan:

    PLANS_MAP = {
        "absolute": scan,
        "relative": rel_scan,
        "list_scan": list_scan,
        "grid_scan": grid_scan,
        "count": None,
    }

    COUNTERS_MAP = {
        "EpicsSignalRO": EpicsSignalRO,
        "pilatus300k": Pilatus,
        "pilatus6ROIs": Pilatus6ROIs,
    }

    def __init__(self, daf_scan_inputs: DAFScanInputs) -> None:
        self.scan_data = daf_scan_inputs.scan_data
        self.motors = daf_scan_inputs.inputed_motors
        self.motors_data_dict = daf_scan_inputs.motors_data_dict
        self.counters = daf_scan_inputs.counters
        self.main_counter = (
            daf_scan_inputs.main_counter
            if daf_scan_inputs.main_counter in self.counters
            else None
        )
        self.scan_type = daf_scan_inputs.scan_type
        self.steps = daf_scan_inputs.steps
        self.acquisition_time = daf_scan_inputs.acquisition_time
        self.delay_time = daf_scan_inputs.delay_time
        self.output = create_unique_file_name(daf_scan_inputs.output)
        self.kafka_topic = daf_scan_inputs.kafka_topic
        self.scan_db = daf_scan_inputs.scan_db
        self.PLANS_MAP["count"] = functools.partial(
            count, num=int(1e6), delay=self.acquisition_time
        )  # gambiarra pro count
        self.configure_run_engine()
        self.producer = KafkaProducer()

    def configure_run_engine(self):
        """Instantiate RunEngine and subscribe the needed callbacks"""
        self.RE = RunEngine(context_managers=[DAFSigIntHandler])
        # self.RE.waiting_hook = ProgressBarManager()
        self.instantiate_callbacks()
        self.subscribe_callbacks()

    def configure_metadata(self) -> dict:
        """Configure base metada for scans"""
        md = {}
        path, file = os.path.split(self.output)
        md["file_name"] = file
        md["file_path"] = path
        if self.motors:
            md["main_motor"] = self.motors[0]
        if self.main_counter is not None:
            md["main_counter"] = self.main_counter
        return md

    def instantiate_callbacks(self):
        """Instantiate all callbacks and store then in a dict"""
        self.callbacks = {}
        self.callbacks["bec"] = BestEffortCallback()
        # self.callbacks["nexus"] = self.nexus_callback()
        self.callbacks["kafka"] = self.kafka_callback
        self.callbacks["db"] = self.config_databroker()
        # self.callbacks["debug"] = self.debug_callback

    def subscribe_callbacks(self):
        """Subscribe all callbacks to the RunEngine"""
        self.callback_tokens = {}
        for callback_name, callback in self.callbacks.items():
            self.callback_tokens[callback_name] = self.RE.subscribe(callback)

    def config_databroker(self):
        """Databroker to write"""
        self.db = databroker.Broker.named(self.scan_db)
        return self.db.insert

    def debug_callback(self, name: str, doc: dict):
        """Callback for debug only, too much verbose"""
        print(name, doc)

    def nexus_callback(self):
        """Callback to write NeXus files right after the plan is executed"""
        nxwriter = NXWriter()
        nxwriter.file_name = self.output
        nxwriter.warn_on_missing_content = False
        return nxwriter.receiver

    def nexus_export(self, scan_hash: str):
        nxwriter = NXWriter()
        nxwriter.file_name = self.output
        nxwriter.warn_on_missing_content = False
        au.replay(self.db[scan_hash], nxwriter.receiver)

    def kafka_callback(self, name: str, doc: dict):
        """Callback to stream Bluesky Documents via Kafka"""
        self.producer = KafkaProducer(value_serializer=msgpack.dumps)
        self.producer.send(self.kafka_topic, (name, doc))

    def configure_scan(self):
        """Build motors, counters and the plan"""
        self.build_ophyd_motors()
        self.build_counters()
        bluesky_plan_args = self.build_scan_args()
        return self.get_plan(bluesky_plan_args)

    def build_ophyd_motors(self):
        """Build ophyd motors used in the scan"""
        self.ophyd_motors = {}
        for motor in self.motors:
            self.ophyd_motors[motor] = EpicsMotor(
                self.motors_data_dict[motor]["pv"], name=motor
            )
            self.ophyd_motors[motor].wait_for_connection(timeout=10)

    def build_counters(self):
        """Build counters used in the scan based in the configuration file"""
        self.ophyd_counters = {}
        for counter, counter_info in self.counters.items():
            if counter_info["type"] == "AD":
                path_to_write = os.path.dirname(self.output)
                self.ophyd_counters[counter] = self.COUNTERS_MAP[counter_info["class"]](
                    counter_info["pv"],
                    name=counter,
                    write_path=path_to_write,
                    read_attrs=["hdf5"],
                )
                self.ophyd_counters[counter].cam.acquire_period.put(
                    self.acquisition_time
                )
                self.ophyd_counters[counter].cam.acquire_time.put(self.acquisition_time)
                self.ophyd_counters[counter].cam.num_images.put(1)
                continue
            self.ophyd_counters[counter] = self.COUNTERS_MAP[counter_info["class"]](
                counter_info["pv"], name=counter
            )

    def build_scan_args(self):
        """Build the points and motors inputed to the plan. This method can be overriden by the calling class"""
        movables = []
        for motor_name, ophyd_motor in self.ophyd_motors.items():
            movables.append(ophyd_motor)
            for i in self.scan_data[motor_name]:
                movables.append(i)
        if self.steps is not None:
            movables.append(self.steps)
        return movables

    def get_plan(self, bluesky_plan_args: list):
        """Get the plan that's going to be used based in the scan_type argument"""
        return self.PLANS_MAP[self.scan_type](
            [*self.ophyd_counters.values()], *bluesky_plan_args
        )

    @staticmethod
    def convert_to_float_if_not_none(val: "float or tuple"):
        """Method to convert from numpy data to python standard data. otherwise it will broke the .yml file"""
        if isinstance(val, tuple):
            result = []
            for item in val:
                if item is not None:
                    result.append(float(item))
            return result
        else:
            if val is not None:
                return float(val)

    def write_stats(self):
        self.io = du.DAFIO(read=False)
        self.experiment_file_dict = self.io.read()
        stats = ("com", "cen", "max", "min", "fwhm")
        stat_dict = {}
        # print(self.callbacks["bec"].peaks)
        for key in stats:
            stat_dict[key] = {}
            for counter_name, stats in self.callbacks["bec"].peaks[key].items():
                stat_dict[key][counter_name] = self.convert_to_float_if_not_none(stats)
        # for counter, counter_info in self.counters.items():
        #     if counter_info["type"] == "AD":
        #         continue
        #     stat_dict[counter] = {}
        #     stat_dict[counter]["peak"] = self.convert_to_float_if_not_none(
        #         self.callbacks["bec"].peaks["max"][counter][1]
        #     )
        #     stat_dict[counter]["peak_at"] = self.convert_to_float_if_not_none(
        #         self.callbacks["bec"].peaks["max"][counter][0]
        #     )
        #     stat_dict[counter]["FWHM"] = self.convert_to_float_if_not_none(
        #         self.callbacks["bec"].peaks["fwhm"][counter]
        #     )
        #     # stat_dict[counter]["FWHM_at"] = self.callbacks["bec"].peaks["fwhm"][counter][0]
        #     stat_dict[counter]["COM"] = self.convert_to_float_if_not_none(
        #         self.callbacks["bec"].peaks["com"][counter]
        #     )
        self.experiment_file_dict["scan_stats"] = stat_dict
        self.io.write(self.experiment_file_dict)

    def run(self):
        """Run the scan and export to a NeXus file"""
        md = self.configure_metadata()
        scan_hash = self.RE(self.configure_scan(), **md)
        self.nexus_export(scan_hash)
        self.write_stats()
