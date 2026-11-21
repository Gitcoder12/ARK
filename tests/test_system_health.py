from types import SimpleNamespace

import pytest

from utils import system_health


def test_health_report_is_json_serializable(monkeypatch):
    monkeypatch.setattr(system_health.psutil, "virtual_memory", lambda: SimpleNamespace(
        total=16 * system_health._GIB, available=8 * system_health._GIB, percent=50.0
    ))
    monkeypatch.setattr(system_health.psutil, "cpu_count", lambda logical=True: 8 if logical else 4)
    monkeypatch.setattr(system_health.psutil, "cpu_percent", lambda interval=None: 12.5)
    monkeypatch.setattr(system_health.shutil, "disk_usage", lambda path: SimpleNamespace(
        total=100 * system_health._GIB, used=40 * system_health._GIB, free=60 * system_health._GIB
    ))
    monkeypatch.setattr(system_health, "get_gpu_info", lambda: {
        "available": False, "backend": None, "device_count": 0,
        "total_vram_gb": 0.0, "devices": [], "error": "not installed"
    })
    report = system_health.get_system_health()
    assert report["memory"]["total_gb"] == 16.0
    assert report["cpu"]["logical_cores"] == 8
    assert report["disk"]["free_gb"] == 60.0
    assert '"status": "ok"' in system_health.health_json()


def test_requirements_pass_when_resources_are_sufficient(monkeypatch):
    monkeypatch.setattr(system_health.psutil, "virtual_memory", lambda: SimpleNamespace(
        available=8 * system_health._GIB
    ))
    monkeypatch.setattr(system_health.shutil, "disk_usage", lambda path: SimpleNamespace(
        free=50 * system_health._GIB
    ))
    assert system_health.check_requirements(4, 20) is True


def test_requirements_fail_when_resources_are_insufficient(monkeypatch):
    monkeypatch.setattr(system_health.psutil, "virtual_memory", lambda: SimpleNamespace(
        available=2 * system_health._GIB
    ))
    monkeypatch.setattr(system_health.shutil, "disk_usage", lambda path: SimpleNamespace(
        free=5 * system_health._GIB
    ))
    assert system_health.check_requirements(4, 20) is False


def test_negative_thresholds_raise():
    with pytest.raises(ValueError):
        system_health.check_requirements(-1, 1)
