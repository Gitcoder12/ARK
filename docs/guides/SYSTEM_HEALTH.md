# System Health Preflight

The shared utility reports host resources before an agent or model workload starts.

```python
from utils.system_health import check_requirements, get_system_health, health_json

report = get_system_health()       # JSON-serializable dictionary
print(health_json())               # formatted JSON string

if not check_requirements(min_ram_gb=8, min_disk_gb=10):
    raise RuntimeError("Insufficient available RAM or disk space")
```

Install the project dependencies to enable CPU, memory and disk inspection. GPU inspection
uses PyTorch when available and falls back to optional GPUtil (`pip install GPUtil`).

**Important:** this is a best-effort preflight snapshot, not a guarantee against out-of-memory
errors. Available resources can change immediately, and GPU memory reporting depends on the
installed driver/runtime. Use workload-specific VRAM estimates and runtime limits as well.
