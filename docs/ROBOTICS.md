# ARK Robotics

ARK Robotics adds a hardware-agnostic supervision layer for embodied-agent research.
It is separate from the existing ARKWorld / Robopia digital-commons simulation.

## Components

- `RobotObservation`: bounded sensor, workspace and emergency-stop snapshot.
- `RobotCommand`: one proposed primitive action.
- `SafetyPolicy`: allow-list, workspace, velocity, force, duration and episode-budget checks.
- `RobotSupervisor`: the only supported path from a proposed action to an adapter.
- `RobotAdapter`: interface for a simulator or hardware-specific transport.
- `MockRobotAdapter`: in-memory demo adapter; it never connects to hardware.

## Quick start

```python
from ark.robotics import MockRobotAdapter, RobotCommand, RobotSupervisor

adapter = MockRobotAdapter()
supervisor = RobotSupervisor()
command = RobotCommand(
    action="move", target={"x": 0.1, "y": 0.0, "z": 0.2},
    velocity=0.1, force=2.0, duration=0.5,
)

# The first call is blocked pending explicit approval.
pending = supervisor.execute(adapter, command)
assert pending["decision"]["requires_approval"]

# Pass approved=True only after obtaining real human approval.
result = supervisor.execute(adapter, command, approved=True)
assert result["execution"]["status"] == "simulated"
```

## Adding a simulator or robot

Implement `RobotAdapter.observe`, `execute` and `stop`. Convert vendor-specific
messages into the shared contracts. Keep vendor SDKs in optional extras or separate
integration packages; ARK core has no ROS, camera, robot or cloud dependency.

Every command is checked immediately before execution. Unknown actions, out-of-range
targets, invalid limits, active emergency stops and exhausted episode budgets fail
closed. Human approval is required by default.

## Safety boundary

This is a research integration scaffold, not a certified robot-safety system. The
software supervisor is not a substitute for a physical emergency-stop circuit,
safety-rated controller, risk assessment, guarded workspace or trained operator.
Do not connect an actuator until the adapter has independent hardware interlocks,
validated units, calibration, speed/force limits and simulator/hardware-in-loop tests.
