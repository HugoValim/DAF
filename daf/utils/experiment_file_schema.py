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


REQUIRED_TOP_LEVEL_KEYS = frozenset(ExperimentFile.__annotations__)

VECTOR_FIELDS = frozenset(
    {
        "IDir",
        "IDir_print",
        "NDir",
        "NDir_print",
        "RDir",
        "hklnow",
    }
)
MATRIX_FIELDS = frozenset({"U_mat", "UB_mat"})
CONSTRAINT_FIELDS = frozenset(
    {
        "cons_mu",
        "cons_eta",
        "cons_chi",
        "cons_phi",
        "cons_nu",
        "cons_del",
        "cons_alpha",
        "cons_beta",
        "cons_psi",
        "cons_omega",
        "cons_qaz",
        "cons_naz",
    }
)
NUMERIC_FIELDS = frozenset(
    {
        "energy_offset",
        "twotheta",
        "theta",
        "alpha",
        "qaz",
        "naz",
        "tau",
        "psi",
        "beta",
        "omega",
        "lparam_a",
        "lparam_b",
        "lparam_c",
        "lparam_alpha",
        "lparam_beta",
        "lparam_gama",
        "Max_diff",
        "PV_energy",
    }
) | CONSTRAINT_FIELDS
STRING_FIELDS = frozenset(
    {
        "Mode",
        "Material",
        "Sampleor",
        "Print_marker",
        "Print_cmarker",
        "Print_space",
        "scan_name",
        "separator",
        "macro_file",
        "setup",
        "setup_desc",
        "default_counters",
        "current_scan_file",
        "main_scan_motor",
        "kafka_topic",
        "scan_db",
        "version",
    }
)
BOOL_FIELDS = frozenset({"macro_flag", "scan_running", "simulated"})
INT_FIELDS = frozenset({"dark_mode"})
DICT_FIELDS = frozenset({"user_samples", "scan_stats"})
LIST_FIELDS = frozenset({"reflections", "scan_counters"})


class ExperimentFileValidationError(ValueError):
    """Raised when a loaded .Experiment file does not match the expected schema."""


def validate_experiment_file(data: Any) -> ExperimentFile:
    """Validate loaded .Experiment YAML data and return it typed for callers."""
    if not isinstance(data, dict):
        raise ExperimentFileValidationError(".Experiment must contain a YAML mapping")

    for key in sorted(REQUIRED_TOP_LEVEL_KEYS):
        if key not in data:
            raise ExperimentFileValidationError(f"Missing required field: {key}")

    for field in sorted(STRING_FIELDS):
        _require_type(data[field], str, field)
    for field in sorted(NUMERIC_FIELDS):
        _require_number(data[field], field)
    for field in sorted(BOOL_FIELDS):
        _require_type(data[field], bool, field)
    for field in sorted(INT_FIELDS):
        _require_int(data[field], field)
    for field in sorted(DICT_FIELDS):
        _require_type(data[field], dict, field)
    for field in sorted(LIST_FIELDS):
        _require_type(data[field], list, field)
    for field in sorted(VECTOR_FIELDS):
        _require_numeric_sequence(data[field], 3, field)
    for field in sorted(MATRIX_FIELDS):
        _require_matrix(data[field], 3, 3, field)

    _validate_motors(data["motors"])
    _validate_beamline_pvs(data["beamline_pvs"])

    return data


def _require_type(value: Any, expected_type: type, field: str) -> None:
    if not isinstance(value, expected_type):
        raise ExperimentFileValidationError(
            f"Invalid field {field}: expected {expected_type.__name__}"
        )


def _require_int(value: Any, field: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ExperimentFileValidationError(f"Invalid field {field}: expected int")


def _require_number(value: Any, field: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ExperimentFileValidationError(f"Invalid field {field}: expected number")


def _require_bool_like(value: Any, field: str) -> None:
    if isinstance(value, bool):
        return
    if isinstance(value, int) and value in (0, 1):
        return
    raise ExperimentFileValidationError(
        f"Invalid field {field}: expected bool or 0/1"
    )


def _require_numeric_sequence(value: Any, length: int, field: str) -> None:
    if not isinstance(value, list) or len(value) != length:
        raise ExperimentFileValidationError(
            f"Invalid field {field}: expected list with {length} numbers"
        )
    for index, item in enumerate(value):
        _require_number(item, f"{field}.{index}")


def _require_matrix(value: Any, rows: int, columns: int, field: str) -> None:
    if not isinstance(value, list) or len(value) != rows:
        raise ExperimentFileValidationError(
            f"Invalid field {field}: expected {rows}x{columns} numeric matrix"
        )
    for row_index, row in enumerate(value):
        _require_numeric_sequence(row, columns, f"{field}.{row_index}")


def _validate_motors(value: Any) -> None:
    _require_type(value, dict, "motors")
    if not value:
        raise ExperimentFileValidationError("Invalid field motors: expected entries")

    for name, motor in value.items():
        field = f"motors.{name}"
        _require_type(motor, dict, field)
        _require_entry_key(motor, "pv", field)
        _require_entry_key(motor, "value", field)
        _require_entry_key(motor, "bounds", field)
        _require_entry_key(motor, "up", field)
        _require_type(motor["pv"], str, f"{field}.pv")
        _require_number(motor["value"], f"{field}.value")
        _require_numeric_sequence(motor["bounds"], 2, f"{field}.bounds")
        _require_bool_like(motor["up"], f"{field}.up")


def _validate_beamline_pvs(value: Any) -> None:
    _require_type(value, dict, "beamline_pvs")
    if not value:
        raise ExperimentFileValidationError(
            "Invalid field beamline_pvs: expected entries"
        )

    for name, beamline_pv in value.items():
        field = f"beamline_pvs.{name}"
        _require_type(beamline_pv, dict, field)
        _require_entry_key(beamline_pv, "pv", field)
        _require_entry_key(beamline_pv, "value", field)
        _require_entry_key(beamline_pv, "up", field)
        _require_entry_key(beamline_pv, "simulated", field)
        _require_type(beamline_pv["pv"], str, f"{field}.pv")
        _require_number(beamline_pv["value"], f"{field}.value")
        _require_bool_like(beamline_pv["up"], f"{field}.up")
        _require_bool_like(beamline_pv["simulated"], f"{field}.simulated")


def _require_entry_key(entry: dict[str, Any], key: str, field: str) -> None:
    if key not in entry:
        raise ExperimentFileValidationError(f"Missing required field: {field}.{key}")
