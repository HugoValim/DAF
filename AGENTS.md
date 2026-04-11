# DAF - Diffractometer Angles Finder

## Project Overview

**DAF** is a Python package for controlling synchrotron beamline diffractometers, developed at **LNLS (Brazilian National Synchrotron Light Laboratory)**, part of the Brazilian Center for Research in Energy and Materials (CNPEM).

The project provides both a **command-line interface (CLI)** and a **GUI** for:
- Controlling multi-axis X-ray diffractometers
- Computing crystal orientation matrices (U and UB matrices)
- Performing HKL scans and reciprocal space mapping
- Managing experiment configurations for X-ray diffraction at synchrotron beamlines

## Project Type

Scientific/Research Software - X-ray diffraction control system for synchrotron beamlines.

## Key Dependencies

- **xrayutilities** - X-ray physics calculations, materials database
- **bluesky/ophyd** - EPICS-aware device control (synchrotron hardware)
- **pyepics** - EPICS channel access
- **numpy/scipy** - Numerical computations
- **pandas** - Data handling
- **matplotlib** - Visualization
- **h5py** - HDF5 file I/O
- **kafka-python** - Kafka messaging for scan data
- **qdarkstyle** - Dark theme for GUI

## Package Structure

```
daf/
├── core/                  # Core calculation engines
│   ├── main.py            # DAF main class - orchestrates all functionality
│   ├── ub_matrix_calc.py  # U/UB matrix calculations for crystal orientation
│   ├── minimization.py    # Minimization procedures for angle solving
│   ├── reciprocal_map.py # Reciprocal space mapping window
│   ├── matrix_utils.py   # Rotation matrix calculations for diffractometer angles
│   ├── math_utils.py     # Mathematical utilities (vector angles, etc.)
│   └── utils.py          # MODE_COLUMNS definitions and sample definitions
│
├── command_line/          # CLI commands
│   ├── experiment/        # Experiment configuration commands
│   │   ├── experiment_configuration.py  # daf.expt - set material, energy, lattice
│   │   ├── operation_mode.py             # daf.mode - set diffractometer mode
│   │   ├── bounds.py                     # daf.bounds - set angle limits
│   │   ├── mode_constraints.py           # daf.cons - set constraint values
│   │   ├── set_u_ub_matrix.py            # daf.ub - calculate/display U and UB
│   │   └── manage_counters.py            # daf.mc - manage scan counters
│   │
│   ├── move/             # Movement commands
│   │   ├── ang_move.py           # daf.amv - move by angle
│   │   ├── hkl_move.py           # daf.mv - move by HKL coordinates
│   │   ├── hkl_calc.py           # daf.ca - HKL calculation display
│   │   ├── rel_ang_move.py       # daf.ramv - relative angle move
│   │   └── reciprocal_space_map.py # daf.rmap - reciprocal space map GUI
│   │
│   ├── query/            # Query/status commands
│   │   ├── status.py             # daf.status - display current configuration
│   │   └── where.py              # daf.wh - show current HKL position
│   │
│   ├── scan/             # Scan commands (a1scan, d1scan, mesh, hkl_scan, etc.)
│   │   └── [multiple scan variants]
│   │
│   └── support/          # Utility/support commands
│       ├── init.py              # daf.init - initialize DAF environment
│       ├── setup.py             # daf.setup - manage saved environments
│       ├── reset.py             # daf.reset - reset to defaults
│       ├── gui_all.py           # daf.guiall - launch full GUI
│       └── fetch_pvs.py         # daf.fetch - fetch EPICS process variables
│
├── gui/                  # PyQt-based GUI
│   ├── main_window.py    # Main GUI window
│   ├── main_tabs/        # Tab widgets (Status, Position, Scan, Setup, Rmap)
│   ├── windows/          # Popup windows (experiment, sample, bounds, goto_hkl)
│   └── scripts/          # GUI entry points (daf_gui_caller, live_view_caller)
│
├── config/               # Configuration files
│   ├── motors_real_config.py   # Real motor configurations
│   ├── motors_sim_config.py    # Simulated motor configurations
│   ├── beamline_pvs_real.py    # Real EPICS PVs
│   ├── beamline_pvs_sim.py     # Simulated EPICS PVs
│   └── counters_config.py      # Counter definitions
│
└── utils/                # Utility modules
    ├── dafutilities.py   # DAFIO class for file I/O
    ├── daf_paths.py      # Path management
    ├── experiment_configs.py # Experiment state persistence
    └── print_utils.py    # Table printing utilities
```

## Core Concepts

### Diffractometer Angles
DAF controls a 6-circle diffractometer with these motor angles:
- **Mu (μ)** - Sample rotation
- **Eta (η)** - Sample tilt
- **Chi (χ)** - Crystal orientation
- **Phi (φ)** - Phi rotation
- **Nu (ν)** - Detector vertical
- **Del (δ)** / **Delta** - Detector horizontal (2θ equivalent)

### Pseudo Angles
Derived/calculated angles used in crystallography:
- **Alpha, Beta** - Incident/reflection angles
- **Psi, Tau** - Angular parameters
- **Qaz, Naz** - Q-vector azimuthal/normal angles
- **Omega** - Rotation angle

### HKL Miller Indices
The reciprocal space coordinates (H, K, L) that define crystal lattice positions.

### Operation Modes
DAF supports configurable diffractometer modes (like SPEC) defined by 5 digits specifying:
1. Detector constraint (Del/Nu/Qaz/Naz/Zone/Energy)
2. Angle constraint (alpha=beta/alpha/beta/psi)
3. Sample constraint (omega/eta/mu/chi/phi/eta=del/2/mu=nu/2)
4-5. Additional constraints

Example modes:
- `215` = Nu fixed, Alpha=Beta, Eta=Del/2
- `21200` = Nu fixed, alpha=beta, eta fixed

### U and UB Matrices
- **U matrix**: Crystal orientation relative to diffractometer
- **UB matrix**: U × B (where B is the metric tensor for lattice parameters)

Used to transform between laboratory frame and reciprocal space (HKL).

## CLI Commands Reference

| Command | Purpose |
|---------|---------|
| `daf.init` | Initialize DAF environment |
| `daf.expt` | Set experiment (material, energy, lattice) |
| `daf.mode` | Set diffractometer operation mode |
| `daf.bounds` | Set angle limits |
| `daf.cons` | Set constraint values |
| `daf.ub` | Calculate U/UB matrices |
| `daf.mc` | Manage counters |
| `daf.amv` | Move by angle |
| `daf.mv` | Move by HKL |
| `daf.wh` | Show current HKL position |
| `daf.status` | Show all configuration |
| `daf.scan` | Perform HKL scan |
| `daf.gui` | Launch GUI |

## Key Classes

### `daf.core.main.DAF`
The central class that inherits from:
- `MinimizationProc` - Solves for motor angles given HKL targets
- `ReciprocalMapWindow` - GUI for reciprocal space visualization

Main methods for angle solving and HKL movement.

### `daf.core.ub_matrix_calc.UBMatrix`
Handles U and UB matrix calculations from reflections.

### `daf.utils.dafutilities.DAFIO`
File I/O for persisting experiment configurations.

## Workflow Example

```bash
# 1. Initialize
daf.init -6c

# 2. Set experiment (material + energy)
daf.expt -m Si -e 12000

# 3. Set operation mode
daf.mode 215

# 4. Set bounds
daf.bounds -d -180 180 -c -10 100 -l

# 5. Set constraints
daf.cons -n 30 -m 0

# 6. Calculate UB matrix from reflections
daf.ub -r 1 0 0 0 5.28232 0 2 0 10.5647
daf.ub -s

# 7. Move to HKL position
daf.mv 1 1 1

# 8. Perform scan
daf.scan 1 1 1 1.1 1.1 1.1 10
```

## File Formats

- **Experiment configs**: YAML files storing material, energy, mode, bounds, U/UB matrices
- **Counter configs**: YAML files listing detector counters for scans
- **Scan data**: HDF5 format with pandas DataFrames

## Notes for Agents

1. **Hardware vs Simulation**: DAF can run with real EPICS motors (`-6c` flag) or simulated motors (`-s` flag in `daf.init`)

2. **BlueSky Integration**: The project uses Bluesky/ Ophyd for device abstraction, suggesting it's designed to integrate with the Bluesky data acquisition framework used at synchrotrons

3. **XrayUtilities**: Heavily uses `xrayutilities.materials` for crystal lattice definitions and X-ray physics calculations

4. **LNLS Specific**: References to specific beamlines and the Brazilian synchrotron context (LNLS/CNPEM)

5. **Entry Points**: All CLI commands are registered via `setup.py` entry_points as console_scripts
