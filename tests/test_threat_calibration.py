import pytest

from ark.threat import ThreatMeter, calibrate_threat_threshold


def test_calibration_reports_false_positive_and_negative_rates():
    report = calibrate_threat_threshold([0.05, 0.15, 0.55, 0.85], [False, False, True, True])
    assert report.false_positive_rate == 0.0
    assert report.false_negative_rate == 0.0
    assert 0.15 < report.threshold <= 0.55


def test_meter_uses_validation_calibrated_alert_threshold():
    meter = ThreatMeter()
    with pytest.raises(RuntimeError):
        _ = meter.alert
    report = meter.calibrate([0.1, 0.8], [False, True])
    meter.record("hazard_hit")
    assert meter.alert is (meter.score >= report["threshold"])


def test_calibration_rejects_invalid_data():
    with pytest.raises(ValueError):
        calibrate_threat_threshold([], [])
    with pytest.raises(ValueError):
        calibrate_threat_threshold([float("nan")], [True])
    with pytest.raises(ValueError):
        calibrate_threat_threshold([1.1], [True])
