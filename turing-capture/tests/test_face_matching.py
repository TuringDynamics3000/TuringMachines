"""
Test suite for face matching and comparison
"""
import numpy as np
import pytest
from biometrics import compare_embeddings, explain_match, MOBILEFACENET_THRESHOLD, ARCFACE_THRESHOLD


def test_matching_identical_vectors():
    """Test matching with identical vectors"""
    a = np.ones(128, dtype="float32")
    b = np.ones(128, dtype="float32")
    c = np.ones(512, dtype="float32")
    d = np.ones(512, dtype="float32")

    result = compare_embeddings(a, b, c, d)
    assert result["is_match"] == True
    assert result["mobile_score"] > 0.99
    assert result["arcface_score"] > 0.99
    assert result["fused_score"] > 0.99


def test_non_matching_vectors():
    """Test matching with opposite vectors"""
    a = np.ones(128, dtype="float32")
    b = -np.ones(128, dtype="float32")
    c = np.ones(512, dtype="float32")
    d = -np.ones(512, dtype="float32")

    result = compare_embeddings(a, b, c, d)
    assert result["is_match"] == False
    assert result["mobile_score"] < 0.0
    assert result["arcface_score"] < 0.0


def test_matching_output_structure():
    """Test that matching returns expected structure"""
    a = np.ones(128, dtype="float32")
    b = np.ones(128, dtype="float32")
    c = np.ones(512, dtype="float32")
    d = np.ones(512, dtype="float32")

    result = compare_embeddings(a, b, c, d)
    assert "mobile_score" in result
    assert "arcface_score" in result
    assert "fused_score" in result
    assert "is_match" in result
    assert isinstance(result["mobile_score"], float)
    assert isinstance(result["arcface_score"], float)
    assert isinstance(result["fused_score"], float)
    assert isinstance(result["is_match"], bool)


def test_matching_score_range():
    """Test that matching scores are in valid range"""
    a = np.random.randn(128).astype("float32")
    b = np.random.randn(128).astype("float32")
    c = np.random.randn(512).astype("float32")
    d = np.random.randn(512).astype("float32")

    result = compare_embeddings(a, b, c, d)
    assert -1.0 <= result["mobile_score"] <= 1.0
    assert -1.0 <= result["arcface_score"] <= 1.0
    assert -1.0 <= result["fused_score"] <= 1.0


def test_matching_threshold_logic():
    """Test dual-threshold matching logic"""
    # Both scores above threshold
    a = np.ones(128, dtype="float32")
    b = np.ones(128, dtype="float32")
    c = np.ones(512, dtype="float32")
    d = np.ones(512, dtype="float32")
    result = compare_embeddings(a, b, c, d)
    assert result["is_match"] == True

    # MobileFaceNet below threshold
    a = np.ones(128, dtype="float32")
    b = np.zeros(128, dtype="float32")  # Low similarity
    c = np.ones(512, dtype="float32")
    d = np.ones(512, dtype="float32")
    result = compare_embeddings(a, b, c, d)
    # Should fail because mobile score is too low
    assert result["mobile_score"] < MOBILEFACENET_THRESHOLD


def test_explain_match_success():
    """Test explainability for successful match"""
    result = {
        "mobile_score": 0.85,
        "arcface_score": 0.90,
        "fused_score": 0.88,
        "is_match": True
    }
    explanation = explain_match(result)
    assert explanation["summary"] == "match"
    assert len(explanation["reasons"]) > 0
    assert explanation["reasons"][0]["type"] == "match_success"


def test_explain_match_failure_mobile():
    """Test explainability for MobileFaceNet failure"""
    result = {
        "mobile_score": 0.40,  # Below threshold
        "arcface_score": 0.90,
        "fused_score": 0.72,
        "is_match": False
    }
    explanation = explain_match(result)
    assert explanation["summary"] == "no_match"
    assert any(r["type"] == "mobilefacenet_low_match" for r in explanation["reasons"])


def test_explain_match_failure_arcface():
    """Test explainability for ArcFace failure"""
    result = {
        "mobile_score": 0.85,
        "arcface_score": 0.30,  # Below threshold
        "fused_score": 0.52,
        "is_match": False
    }
    explanation = explain_match(result)
    assert explanation["summary"] == "no_match"
    assert any(r["type"] == "arcface_low_match" for r in explanation["reasons"])


def test_explain_match_failure_both():
    """Test explainability for both models failing"""
    result = {
        "mobile_score": 0.40,
        "arcface_score": 0.30,
        "fused_score": 0.34,
        "is_match": False
    }
    explanation = explain_match(result)
    assert explanation["summary"] == "no_match"
    assert len(explanation["reasons"]) == 2  # Both should fail
