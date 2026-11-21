"""Host resource preflight checks for AI and automation workloads.

The checks are estimates, not guarantees: other processes can consume resources
after a check, and GPU/runtime-specific allocations may differ from reported VRAM.
"""
from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from typing import Any

import psutil

_GIB = 1024 ** 3


def _gb(value: int | float) -> float:
    return round(float(value) / _GIB, 2)


def get_gpu_info() -> dict[str, Any]:
    """Return JSON-safe GPU availability and VRAM information.

    PyTorch is preferred when installed. GPUtil is used as a fallback. Neither
    package is required to import this module.
    """
    try:
        import torch  # type: ignore[import-not-found]

        if torch.cuda.is_available():
            devices = []
            for index in range(torch.cuda.device_count()):
                props = torch.cuda.get_device_properties(index)
                total = int(props.total_memory)
                try:
                    free, total_runtime = torch.cuda.mem_get_info(index)
                    free_bytes = int(free)
                    total = int(total_runtime)
                except Exception:
                    free_bytes = None
                devices.append(
                    {
                        "index": index,
                        "name": str(props.name),
                        "total_vram_gb": _gb(total),
                        "free_vram_gb": _gb(free_bytes) if free_bytes is not None else None,
                    }
                )
            return {
                "available": bool(devices),
                "backend": "torch",
                "device_count": len(devices),
                "total_vram_gb": round(sum(d["total_vram_gb"] for d in devices), 2),
                "devices": devices,
                "error": None,
            }
    except ImportError:
        pass
    except Exception:
        pass

    try:
        import GPUtil  # type: ignore[import-not-found]

        devices = []
        for gpu in GPUtil.getGPUs():
            devices.append(
                {
                    "index": int(gpu.id),
                    "name": str(gpu.name),
                    "total_vram_gb": round(float(gpu.memoryTotal) / 1024, 2),
                    "free_vram_gb": round(float(gpu.memoryFree) / 1024, 2),
                }
            )
        return {
            "available": bool(devices),
            "backend": "GPUtil",
            "device_count": len(devices),
            "total_vram_gb": round(sum(d["total_vram_gb"] for d in devices), 2),
            "devices": devices,
            "error": None,
        }
    except ImportError:
        return {
            "available": False,
            "backend": None,
            "device_count": 0,
            "total_vram_gb": 0.0,
            "devices": [],
            "error": "GPU inspection unavailable: install torch or GPUtil",
        }
    except Exception as exc:
        return {
            "available": False,
            "backend": "GPUtil",
            "device_count": 0,
            "total_vram_gb": 0.0,
            "devices": [],
            "error": f"{type(exc).__name__}: {exc}",
        }


def get_system_health() -> dict[str, Any]:
    """Collect CPU, memory, disk and GPU details in a JSON-safe dictionary."""
    errors: list[str] = []
    try:
        memory = psutil.virtual_memory()
        memory_info = {
            "total_gb": _gb(memory.total),
            "available_gb": _gb(memory.available),
            "used_percent": float(memory.percent),
        }
    except Exception as exc:
        memory_info = {"total_gb": None, "available_gb": None, "used_percent": None}
        errors.append(f"memory: {type(exc).__name__}: {exc}")

    try:
        cpu_info = {
            "logical_cores": psutil.cpu_count(logical=True),
            "physical_cores": psutil.cpu_count(logical=False),
            "usage_percent": float(psutil.cpu_percent(interval=0.1)),
        }
    except Exception as exc:
        cpu_info = {"logical_cores": None, "physical_cores": None, "usage_percent": None}
        errors.append(f"cpu: {type(exc).__name__}: {exc}")

    try:
        disk_path = Path.cwd().anchor or os.path.abspath(os.sep)
        disk = shutil.disk_usage(disk_path)
        disk_info = {
            "path": disk_path,
            "total_gb": _gb(disk.total),
            "used_gb": _gb(disk.used),
            "free_gb": _gb(disk.free),
        }
    except Exception as exc:
        disk_info = {"path": None, "total_gb": None, "used_gb": None, "free_gb": None}
        errors.append(f"disk: {type(exc).__name__}: {exc}")

    return {
        "status": "ok" if not errors else "partial",
        "memory": memory_info,
        "cpu": cpu_info,
        "disk": disk_info,
        "gpu": get_gpu_info(),
        "errors": errors,
    }


def check_requirements(min_ram_gb: int, min_disk_gb: int) -> bool:
    """Return whether currently available RAM and disk meet the requested minima.

    This is a best-effort preflight check, not a guarantee against OOM or runtime
    failure. Invalid thresholds or failed resource probes return False.
    """
    if min_ram_gb < 0 or min_disk_gb < 0:
        raise ValueError("Resource requirements must be non-negative.")

    try:
        available_ram = psutil.virtual_memory().available
        disk_path = Path.cwd().anchor or os.path.abspath(os.sep)
        available_disk = shutil.disk_usage(disk_path).free
    except (OSError, RuntimeError):
        return False
    except Exception:
        return False

    return available_ram >= min_ram_gb * _GIB and available_disk >= min_disk_gb * _GIB


def health_json(indent: int = 2) -> str:
    """Serialize the current health report as JSON."""
    return json.dumps(get_system_health(), indent=indent, sort_keys=True)
