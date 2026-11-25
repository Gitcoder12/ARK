# Runtime Resource Governor

The governor converts optional GPU telemetry into **advisory scheduling decisions**.
It is deliberately hardware-agnostic and has no mandatory NVIDIA, CUDA, ROCm, or
vendor dependency. A telemetry adapter (for example, an NVML-backed collector)
can populate `GPUObservation`; tests and CPU-only installations can use fake or
empty observations.

## Decisions

- **normal**: continue and monitor.
- **pressure**: apply queue backpressure, reduce concurrency, or unload idle
  models when the serving layer confirms they are safe to unload.
- **thermal_pause**: stop admitting new GPU work and let in-flight work drain
  when the observed temperature reaches the critical threshold.
- **unknown**: collect telemetry; missing values are never treated as zero.

The module does not schedule arbitrary rest periods. GPUs can run continuously
inside their supported thermal and power envelope. Hardware/driver protections
remain authoritative; this module does not manipulate fan curves, clocks, power
limits, or device resets.

## Integration contract

1. Collect timestamped device metrics in an adapter outside this package.
2. Construct a validated `GPUObservation` (leave unavailable metrics as `None`).
3. Pass it to `RuntimeResourceGovernor.evaluate()`.
4. Let the orchestrator apply the returned advisory actions and record the
   observation, decision, and action outcome.
5. Re-evaluate after a short bounded interval; use hysteresis in the collector
   or scheduler before resuming after a thermal pause.

The governor is deterministic and has no background thread, polling loop,
network access, or hardware side effects. Thresholds are configurable through
`GovernorPolicy`. The defaults are conservative starting points, not universal
hardware specifications; tune them against the actual GPU and workload.

## Metrics to add in a production adapter

Temperature, utilization, VRAM used/total, power draw/limit, hardware throttling,
queue depth, request latency, model load/unload duration, and allocation failures.
Track process RSS separately from Python allocations. Never claim that a
`tracemalloc` measurement represents total GPU or process memory.
