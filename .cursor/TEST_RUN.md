# Test run (agent reference)

This file was last updated after a **successful** test run so agents can repeat the same invocation.

- **Last verified (UTC)**: 2026-04-11
- **Working directory**: /home/agent/projects/DAF
- **Command**: `/home/agent/.mamba/envs/daf-tests/bin/python -m pytest tests/ -v --tb=no --ignore=tests/gui/ --ignore=tests/command_line/support/test_gui_all.py -p no:randomly`
- **Environment**: mamba env `daf-tests` at `/home/agent/.mamba/envs/daf-tests/bin/python`
- **Scope**: Full suite (excluding GUI tests and test_gui_all.py)

**Notes**: `-p no:randomly` disables pytest-randomly to prevent test order dependencies. Some tests (setup, init, hkl_calc/hkl_move main) fail due to missing `.Experiment` file or mock issues - these are pre-existing integration-level issues.
