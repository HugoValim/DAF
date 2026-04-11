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
conda env create -f environment.yml
conda activate daf-tests
```

### Testing
```bash
pytest                          # Run all tests
pytest tests/unit_conftest.py    # Run unit tests with EPICS mocks
pytest -m "not slow"             # Skip slow tests
```

### Linting (pre-commit)
```bash
pre-commit run --all-files       # Run all hooks
pre-commit run black --all-files
pre-commit run flake8 --all-files
```

## Architecture

### Core Engine
- **`daf.core.main.DAF`** - Central class inheriting from `MinimizationProc` and `ReciprocalMapWindow`
  - Handles angle solving (minimization) and reciprocal space visualization
  - Uses `xrayutilities` for X-ray physics and crystal calculations
  - Builds xrd experiment via `xu.HXRD` class

### CLI Command Structure
All CLI commands inherit from `daf.command_line.cli_base_utils.CLIBase`:
1. `parse_command_line()` - Define argparse
2. `run_cmd()` - Execute command (abstract method)
3. `build_exp()` - Instantiate DAF with current experiment config

Commands are registered via `setup.py` entry_points as console_scripts.

### Key Modules
| Module | Purpose |
|--------|---------|
| `daf/core/main.py` | DAF main class, experiment definition |
| `daf/core/ub_matrix_calc.py` | U/UB matrix calculations |
| `daf/core/minimization.py` | Angle minimization solver |
| `daf/core/mode_parser.py` | Mode parsing, predefined materials |
| `daf/core/matrix_utils.py` | Rotation matrix calculations |
| `daf/command_line/cli_base_utils.py` | Base class for all CLI commands |
| `daf/utils/dafutilities.py` | DAFIO - experiment file persistence |

### Data Flow
1. CLI command reads `.Experiment` file via `DAFIO`
2. `CLIBase.build_exp()` creates `DAF` instance with saved state
3. DAF uses `xrayutilities` for HKL ↔ angle conversions
4. Results written back via `DAFIO.write()`

### Experiment File Format
YAML file (`.Experiment`) storing: Mode, Material, lattice params, U/UB matrices, motor positions/bounds, constraints, energy, beamline PVs.

## EPICS Integration

DAF uses EPICS (Experimental Physics and Industrial Control System) for hardware communication:
- Real mode: Connects to actual beamline motors via `pyepics`
- Simulated mode: Uses mock motors from `daf.config.motors_sim_config`
- Tests mock EPICS entirely via `tests/unit_conftest.py`

Initialization (`daf.init -s` for simulated) launches a Docker container running simulated IOC servers.

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
