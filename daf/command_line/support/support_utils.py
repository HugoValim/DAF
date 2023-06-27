from dataclasses import dataclass

import yaml

from daf.command_line.cli_base_utils import CLIBase
import daf.utils.generate_daf_default as gdd
from daf.utils.daf_paths import DAFPaths as dp
import daf.utils.dafutilities as du


class SupportBase(CLIBase):
    @staticmethod
    def write_yaml(dict_, file_path=None) -> None:
        """Method to write to a yaml file"""
        with open(file_path, "w") as file:
            yaml.dump(dict_, file)

    @staticmethod
    def get_motors_beamline_pvs_counters_info(simulated: bool):
        """Get the right motors depending if it is simulated or not"""
        if simulated:
            from daf.config.motors_sim_config import motors
            from daf.config.beamline_pvs_sim import beamline_pvs
        else:
            from daf.config.motors_real_config import motors
            from daf.config.beamline_pvs_real import beamline_pvs
        from daf.config.counters_config import counters_config

        return motors, beamline_pvs, counters_config

    def build_current_file(
        self, simulated: bool, kafka_topic: str = None, scan_db: str = None
    ) -> dict:
        """Create the .Experiment file in the current dir"""
        (
            motors,
            beamline_pvs,
            counters_config,
        ) = self.get_motors_beamline_pvs_counters_info(simulated)
        base_data = gdd.default
        base_data["simulated"] = simulated
        base_data["motors"] = motors
        base_data["beamline_pvs"] = beamline_pvs
        base_data["counters"] = counters_config
        if kafka_topic is not None:
            base_data["kafka_topic"] = kafka_topic
        if scan_db is not None:
            base_data["scan_db"] = scan_db
        return base_data

    def get_offline_motors_and_write(self):
        """Get all motors that are offline and set their up bit so DAF become aware"""
        data = du.fetch_pvs_and_check_for_connection()
        self.io.write(data)

    def write_to_disc(
        self, data: dict, fetch_motors: bool = True, is_global: bool = False
    ):
        """write file to disk"""
        if is_global:
            gdd.generate_file(
                data=data, file_path=dp.DAF_CONFIGS, file_name=dp.DEFAULT_FILE_NAME
            )
        else:
            gdd.generate_file(data=data, file_name=dp.DEFAULT_FILE_NAME)
        if fetch_motors:
            self.get_offline_motors_and_write()
