"""
Test suite for liveness detection
"""
import numpy as np
import pytest
from biometrics import compute_liveness


def mock_landmarks():
    """Generate mock landmark data"""
    mock_pt = lambda: (50.0, 50.0)
    return {
        "left_eye": [mock_pt() for _ in range(6)],
        "right_eye": [mock_pt() for _ in range(6)],
        "mouth": [mock_pt() for _ in range(12)],
        "triad": [mock_pt() for _ in range(3)],
    }


def test_liveness_output_shape():
    """Test that liveness returns expected structure"""
    lm = mock_landmarks()
    result = compute_liveness(lm)
    assert "score" in result
    assert "is_live" in result
    assert "blink_rate" in result
    assert "mouth_ratio" in result
    assert "head_pose_magnitude" in result
    assert "reason" in result
    assert isinstance(result["score"], float)
    assert isinstance(result["is_live"], bool)


def test_liveness_failure_mode():
    """Test liveness with incomplete landmarks"""
    bad = {"left_eye": [], "right_eye": [], "mouth": [], "triad": []}
    result = compute_liveness(bad)
    assert result["is_live"] == False
    assert result["reason"] == "landmark_processing_failed"


def test_liveness_score_range():
    """Test that liveness score is in valid range"""
    lm = mock_landmarks()
    result = compute_liveness(lm)
    assert 0.0 <= result["score"] <= 1.0


def test_liveness_with_blink():
    """Test liveness with blink detection"""
    # Create landmarks with closed eyes (low EAR)
    closed_eye = [(0, 0), (0, 0.05), (0, 0.1), (1, 0), (0, 0.1), (0, 0.05)]
    lm = {
        "left_eye": closed_eye,
        "right_eye": closed_eye,
        "mouth": [(i, i) for i in range(12)],
        "triad": [(0, 0), (1, 0), (2, 0)],
    }
    result = compute_liveness(lm)
    assert result["blink_rate"] < 0.25  # Low EAR indicates blink


def test_liveness_with_mouth_movement():
    """Test liveness with mouth movement"""
    # Create landmarks with open mouth (high MAR)
    open_mouth = [
        (0, 0), (0, 0.5), (0, 1.0), (0, 1.5),
        (0, 2.0), (0, 1.5), (0, 1.0), (0, 0.5),
        (0, 0), (0, 0.5), (1, 0), (0, 0.5)
    ]
    lm = {
        "left_eye": [(i, i) for i in range(6)],
        "right_eye": [(i, i) for i in range(6)],
        "mouth": open_mouth,
        "triad": [(0, 0), (1, 0), (2, 0)],
    }
    result = compute_liveness(lm)
    # MAR should be higher with open mouth
    assert "mouth_ratio" in result
