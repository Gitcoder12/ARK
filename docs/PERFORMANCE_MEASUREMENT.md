# Performance measurement

Use the package benchmark helper to capture repeatable measurements for grid navigation, threat evaluation and agent episodes.
Each result includes raw durations, median, P95, P99, throughput, peak Python
allocation, Python version, platform and caller-supplied workload metadata.

Example workflow: call benchmark("grid_bfs", operation, iterations=30,
warmups=5, workload_units=measured_units, metadata={seed, dataset, commit}),
then pass the result to write_json([...], "artifacts/benchmarks/run.json",
run_metadata={hardware, scenario}).

The JSON is chart-ready. Plot latency percentiles and throughput against workload
size; plot memory separately. Compare baseline and candidate on the same machine,
runtime, seed, dataset and cache state. Keep correctness/output-equivalence checks
beside performance numbers.

Important: peak_python_bytes measures Python-tracked allocations, not total
process RSS, native-library memory or GPU memory. Do not claim a speedup from a
single run or compare unlike workloads.
