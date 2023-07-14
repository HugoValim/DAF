import sys
import os

import pytest
import epics

from daf.command_line.support.init import Init, main
from daf.command_line.experiment.experiment_configuration import ExperimentConfiguration
from daf.command_line.support.reset import Reset
from daf.config.motors_sim_config import PV_PREFIX
from daf.utils.daf_paths import DAFPaths as dp
from daf.utils.build_container import run_container

NUMBER_OF_MOTORS = 40


@pytest.fixture(autouse=True, scope="session")
def build_iocs():
    run_container()


@pytest.fixture(autouse=True, scope="session")
def set_motors_velo_and_acc():
    motor_list = []
    for i in range(NUMBER_OF_MOTORS):
        motor_now = PV_PREFIX + "m" + str(i + 1)
        motor_list.append(motor_now)
    accl_motor_pv_list = [pv + ".ACCL" for pv in motor_list]
    velo_motor_pv_list = [pv + ".VELO" for pv in motor_list]
    epics.caput_many(
        accl_motor_pv_list, [1e-5 for i in accl_motor_pv_list], wait="all"
    )  # Reduce the time needed for the motor to accelerate
    epics.caput_many(
        velo_motor_pv_list, [1e5 for i in velo_motor_pv_list], wait="all"
    )  # Increase max motor velocity
    epics.caput_many(
        motor_list, [0 for i in motor_list], wait="all"
    )  # Return all to position 0
    yield
    epics.caput_many(
        motor_list, [0 for i in motor_list], wait="all"
    )  # Return all to position 0


@pytest.fixture(scope="module", autouse=True)
def init_daf(tmp_path_factory):
    dir = tmp_path_factory.mktemp("daf")
    os.chdir(dir)

    def build_args():
        return ["daf.init", "--simulated"]

    mp = pytest.MonkeyPatch()
    with mp.context() as m:
        m.setattr(sys, "argv", build_args())
        obj = Init()
        obj.run_cmd()
        yield obj
    if os.path.isfile(dp.GLOBAL_EXPERIMENT_DEFAULT):
        os.remove(dp.GLOBAL_EXPERIMENT_DEFAULT)

@pytest.fixture
def init_daf_function(tmp_path_factory):
    dir = tmp_path_factory.mktemp("daf")
    os.chdir(dir)

    def build_args():
        return ["daf.init", "--simulated"]

    mp = pytest.MonkeyPatch()
    with mp.context() as m:
        m.setattr(sys, "argv", build_args())
        obj = Init()
        yield obj
    if os.path.isfile(dp.GLOBAL_EXPERIMENT_DEFAULT):
        os.remove(dp.GLOBAL_EXPERIMENT_DEFAULT)

@pytest.fixture
def init_daf_function_global(tmp_path_factory):
    dir = tmp_path_factory.mktemp("daf")
    os.chdir(dir)

    def build_args():
        return ["daf.init", "--simulated", "-g"]

    mp = pytest.MonkeyPatch()
    with mp.context() as m:
        m.setattr(sys, "argv", build_args())
        obj = Init()
        yield obj
    if os.path.isfile(dp.GLOBAL_EXPERIMENT_DEFAULT):
        os.remove(dp.GLOBAL_EXPERIMENT_DEFAULT)



# @pytest.fixture(autouse=True, scope="module")
# def reset():

#     energy = 1
#     def build_args():
#         return ["daf.reset"]


#     mp = pytest.MonkeyPatch()
#     with mp.context() as m:
#         m.setattr(sys, "argv", build_args())
#         obj = Reset()
#         obj.run_cmd()
#         yield obj


# @pytest.fixture(autouse=True, scope="module")
# def set_energy():

#     energy = 1
#     def build_args():
#         return ["daf.expt", "--energy", str(energy)]


#     mp = pytest.MonkeyPatch()
#     with mp.context() as m:
#         m.setattr(sys, "argv", build_args())
#         obj = ExperimentConfiguration()
#         obj.run_cmd()
#         yield obj

@pytest.fixture(autouse=True, scope="module")
def set_sample():

    energy = 1
    def build_args():
        return ["daf.expt", "-s", "Si"]


    mp = pytest.MonkeyPatch()
    with mp.context() as m:
        m.setattr(sys, "argv", build_args())
        obj = ExperimentConfiguration()
        obj.run_cmd()
        yield obj
    # os.remove(dp.GLOBAL_EXPERIMENT_DEFAULT)

