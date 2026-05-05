"""TypedDict schema for the .Experiment YAML file."""
from __future__ import annotations

from typing import Any, TypedDict


class MotorConfig(TypedDict):
    pv: str
    value: float
    bounds: list[float]
    up: bool


class BeamlinePVConfig(TypedDict):
    pv: str
    value: float
    up: bool
    simulated: bool


class ExperimentFile(TypedDict):
    Mode: str
    Material: str
    IDir: list[float]
    IDir_print: list[float]
    NDir: list[float]
    NDir_print: list[float]
    RDir: list[float]
    Sampleor: str
    energy_offset: float
    hklnow: list[float]
    reflections: list[Any]
    Print_marker: str
    Print_cmarker: str
    Print_space: str
    hkl: Any
    cons_mu: float
    cons_eta: float
    cons_chi: float
    cons_phi: float
    cons_nu: float
    cons_del: float
    cons_alpha: float
    cons_beta: float
    cons_psi: float
    cons_omega: float
    cons_qaz: float
    cons_naz: float
    twotheta: float
    theta: float
    alpha: float
    qaz: float
    naz: float
    tau: float
    psi: float
    beta: float
    omega: float
    U_mat: list[list[float]]
    UB_mat: list[list[float]]
    lparam_a: float
    lparam_b: float
    lparam_c: float
    lparam_alpha: float
    lparam_beta: float
    lparam_gama: float
    Max_diff: float
    scan_name: str
    separator: str
    macro_flag: bool
    macro_file: str
    setup: str
    user_samples: dict[str, Any]
    setup_desc: str
    default_counters: str
    dark_mode: int
    scan_stats: dict[str, Any]
    PV_energy: float
    scan_running: bool
    scan_counters: list[Any]
    current_scan_file: str
    main_scan_counter: Any
    main_scan_motor: str
    simulated: bool
    kafka_topic: str
    scan_db: str
    version: str
    motors: dict[str, MotorConfig]
    beamline_pvs: dict[str, BeamlinePVConfig]
