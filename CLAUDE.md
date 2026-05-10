# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**DAF (Diffractometer Angles Finder)** is a Python package for controlling synchrotron beamline diffractometers, developed at LNLS/CNPEM (Brazil). It provides both CLI and GUI interfaces for:
- Controlling 6-circle X-ray diffractometers (Mu, Eta, Chi, Phi, Nu, Del)
- Computing crystal orientation matrices (U and UB matrices)
- Performing HKL scans and reciprocal space mapping
- Managing experiment configurations for X-ray diffraction

## Common Commands

### Installation
```bash
pip install -e .
conda env create -f environment.yml  # or: mamba env create -f environment.yml
```

### Testing

**Always run tests via the `daf-tests` mamba environment.** Do not use the system Python or other environments.

The project uses a **mamba** environment named `daf-tests`. Use `mamba run` to run tests without activating the environment:

There are two test tiers with different conftest files:

**Unit tests** (EPICS fully mocked, no Docker needed — preferred for development):
```bash
mamba run -n daf-tests pytest tests/ -p no:randomly --ignore=tests/gui/
# The -p no:randomly flag is required to avoid test-order failures
```

**Integration tests** (requires Docker + simulated IOC via `tests/conftest.py`):
```bash
mamba run -n daf-tests pytest tests/                  # Runs all tests including integration
mamba run -n daf-tests pytest -m "not slow"           # Skip slow tests
```

Run a single test file:
```bash
mamba run -n daf-tests pytest tests/core/test_daf_calculations.py -v --tb=short
```

The unit conftest (`tests/unit_conftest.py`) patches `epics`, `pyepics`, and `DAFIO.__init__` at import time. It is not a runnable test file — it's included via pytest's conftest discovery. The integration conftest (`tests/conftest.py`) launches a Docker container with a simulated IOC and calls `daf.init --simulated`.

### Linting (pre-commit)
```bash
pre-commit run --all-files
pre-commit run black --all-files
pre-commit run flake8 --all-files
```

## Architecture

### Core Engine
- **`daf.core.main.DAF`** — Central class inheriting from `MinimizationProc` and `ReciprocalMapWindow`. Holds `self.mode` (a `ModeParser` instance) for bounds, constraints, and fixed motor lists. Builds the xrd experiment via `xu.HXRD`.
- **`daf.core.mode_parser.ModeParser`** — Owns mode logic: `constraint_columns()`, `bounds_for(motor)`, `set_bound(motor, val)`, `fixed_motor_list`, `pseudo_constraints()`. DAF backward-compat properties delegate to `self.mode`.
- **`daf.core.daf_engine_factory.DAFEngineFactory`** — Pure factory with `from_dict(experiment_dict) -> DAF`. No EPICS, no file I/O, unit-testable with a plain dict.

### CLI Command Structure
All CLI commands inherit from `daf.command_line.cli_base_utils.CLIBase`:
1. `parse_command_line()` — Define argparse
2. `run_cmd()` — Execute command (abstract method)
3. `build_exp()` — Delegates to `DAFEngineFactory.from_dict()` with the loaded experiment dict

Commands are registered via `setup.py` entry_points as console_scripts.

### Key Modules
| Module | Purpose |
|--------|---------|
| `daf/core/main.py` | DAF main class, experiment definition; holds `self.mode` (ModeParser) |
| `daf/core/daf_engine_factory.py` | `DAFEngineFactory.from_dict()` — builds DAF from plain experiment dict |
| `daf/core/ub_matrix_calc.py` | U/UB matrix calculations |
| `daf/core/minimization.py` | Angle minimization solver |
| `daf/core/mode_parser.py` | `ModeParser` — bounds, constraints, fixed motors for a mode code |
| `daf/core/matrix_utils.py` | Rotation matrix calculations |
| `daf/core/math_utils.py` | Vector/angle math utilities |
| `daf/core/reciprocal_map.py` | Reciprocal space mapping window |
| `daf/core/cli_formatting.py` | Output formatting for CLI |
| `daf/command_line/cli_base_utils.py` | Base class for all CLI commands; `build_exp()` delegates to `DAFEngineFactory` |
| `daf/utils/dafutilities.py` | DAFIO — EPICS PV communication |
| `daf/utils/experiment_file_store.py` | `ExperimentFileStore` — YAML read/write and numpy serialization |
| `daf/utils/epics_motor_client.py` | `EpicsMotorClient` — EPICS motor position reads/writes |
| `daf/utils/daf_paths.py` | Path resolution (local vs global config) |
| `daf/utils/experiment_configs.py` | Experiment state persistence helpers |
| `daf/utils/print_utils.py` | Table printing utilities |

### Data Flow
1. CLI command reads `.Experiment` file via `ExperimentFileStore`
2. `CLIBase.build_exp()` delegates to `DAFEngineFactory.from_dict()` with the experiment dict
3. `DAFEngineFactory` constructs and configures a `DAF` instance (no EPICS, no file I/O)
4. DAF uses `xrayutilities` for HKL ↔ angle conversions
5. Results written back via `DAFIO.write()` / `ExperimentFileStore`

### Experiment File Format & Path Resolution
YAML file (`.Experiment`) storing: Mode, Material, lattice params, U/UB matrices, motor positions/bounds, constraints, energy, beamline PVs.

`DAFPaths.check_for_local_config()` resolves which file to use:
- Local: `./.Experiment` (takes priority when present)
- Global: `~/.daf/.Experiment` (fallback)

Scan configs live in `~/.daf/scan/`.

## EPICS Integration

DAF uses EPICS (Experimental Physics and Industrial Control System) for hardware communication:
- Real mode: Connects to actual beamline motors via `pyepics`
- Simulated mode: Uses mock motors from `daf.config.motors_sim_config`
- Tests mock EPICS entirely via `tests/unit_conftest.py`

Initialization (`daf.init -s` for simulated) launches a Docker container running simulated IOC servers.

## CLI Commands Reference

| Command | Purpose |
|---------|---------|
| `daf.init` | Initialize DAF environment (`-s` simulated, `-6c` 6-circle) |
| `daf.expt` | Set experiment (material, energy, lattice) |
| `daf.mode` | Set diffractometer operation mode |
| `daf.bounds` | Set angle limits |
| `daf.cons` | Set constraint values |
| `daf.ub` | Calculate/display U/UB matrices |
| `daf.mc` | Manage scan counters |
| `daf.amv` | Move by angle |
| `daf.ramv` | Relative angle move |
| `daf.mv` | Move by HKL |
| `daf.ca` | HKL calculation display (no move) |
| `daf.wh` | Show current HKL position |
| `daf.spos` | Show sample position |
| `daf.status` | Show full configuration |
| `daf.scan` | HKL scan |
| `daf.mesh` | Mesh scan |
| `daf.ascan`/`daf.a2scan`…`daf.a6scan` | Absolute angle scans (1–6 motors) |
| `daf.dscan`/`daf.lup`/`daf.d2scan`…`daf.d6scan` | Relative angle scans |
| `daf.ffscan` | Scan from file |
| `daf.tscan` | Time scan |
| `daf.rmap` | Reciprocal space map GUI |
| `daf.gui` / `daf.guiall` | Launch GUI |
| `daf.live` | Live view |
| `daf.setup` | Manage saved environments |
| `daf.reset` | Reset to defaults |
| `daf.newsample` | Create new sample |
| `daf.fetch` | Fetch EPICS PVs |
| `daf.kafka` | Kafka messaging support |
| `daf.help` | Show command help |

## GUI Structure
- PyQt5-based with qdarkstyle dark theme
- Main window with tabs: Status, Position, Scan, Setup, Rmap
- Separate popup windows for experiment/sample/mode/bounds configuration

## Development Standards

### Workflow
- **TDD (Mandatory)**: Red phase (write failing test first) → Green phase (minimal implementation) → Refactor phase
- **One change at a time**: Small, atomic iterations; deliver each step as a working, testable increment
- **Atomic commits**: Follow Conventional Commits format `<type>(<scope>): <description>` (feat, fix, refactor, test, docs, chore, etc.)

### Code Quality
- **Type checking**: Run `mypy --strict`; mandatory type hints for all signatures
- **Linting**: `black`, `flake8`/`ruff`, `isort` for PEP8 compliance
- **No bare `print()`**: Use `logging` module with lazy formatting
- **No magic values**: Extract into named constants or enums
- **Functions**: Keep small and focused (~30 statements max); extract if larger
- **Dead code**: Remove rather than commenting out

### Python Standards
- Python 3.10+ with `pathlib` for paths
- Google-style docstrings for public modules/classes/functions
- Use `dataclasses` or `pydantic` over generic dictionaries
- Resource management via context managers (`with`)
- Define `__all__` in modules with stable public surfaces

### Testing
- **pytest** exclusively; fixtures over deep class hierarchies
- **100% coverage** of business logic and decision paths
- Property-based tests with `hypothesis` for combinatorial input spaces
- Tests must be independent; no shared mutable state

### Security
- **No secrets** in code: use environment variables
- **Input validation**: Sanitize all external inputs (PV values, file paths, network payloads)
- **Injection guards**: Parameterized queries, avoid `shell=True` subprocesses
- Pre-commit hooks for secrets detection

### EPICS-Specific
- Validate PV types and array bounds at boundaries
- Document shared state and locking for concurrent access
- Know CA vs PVA distinction; use appropriate types
- Consider IOC init order, shutdown, and restart behavior

### Performance
- Measure first (profile/benchmark) before optimizing
- Document performance-sensitive areas
- Prefer algorithmic improvements over micro-optimizations

### Documentation
- Explain **why**, not what (in comments and docs)
- Use `TODO(name):` and `FIXME(name):` with owner attribution
- Keep README current with quick start and architecture

## Operation Modes
DAF uses 5-digit mode codes (like SPEC) defining diffractometer constraints:
- Mode `215` = Nu fixed, Alpha=Beta, Eta=Del/2
- Mode `2052` = Nu fixed, alpha=beta, eta fixed, mu fixed
