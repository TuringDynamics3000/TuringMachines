"""
Test suite for embedding generation and normalization
"""
import numpy as np
import pytest
from biometrics import _mock_embedding, _normalize, _cosine


def test_mock_embedding_dimensions_128():
    """Test that mock embedding returns correct dimensions for MobileFaceNet"""
    v = _mock_embedding(128)
    assert isinstance(v, np.ndarray)
    assert v.shape == (128,)
    assert v.dtype == np.float32


def test_mock_embedding_dimensions_512():
    """Test that mock embedding returns correct dimensions for ArcFace"""
    v = _mock_embedding(512)
    assert isinstance(v, np.ndarray)
    assert v.shape == (512,)
    assert v.dtype == np.float32


def test_mock_embedding_deterministic():
    """Test that mock embeddings are deterministic"""
    v1 = _mock_embedding(128)
    v2 = _mock_embedding(128)
    assert np.allclose(v1, v2)


def test_normalize():
    """Test L2 normalization"""
    v = np.array([3.0, 4.0], dtype="float32")
    n = _normalize(v)
    assert abs(np.linalg.norm(n) - 1.0) < 1e-6


def test_normalize_zero_vector():
    """Test normalization of zero vector"""
    v = np.zeros(128, dtype="float32")
    n = _normalize(v)
    assert np.allclose(n, v)  # Should return original


def test_cosine_self_similarity():
    """Test that cosine similarity of vector with itself is 1.0"""
    v = _mock_embedding(128)
    similarity = _cosine(v, v)
    assert abs(similarity - 1.0) < 1e-6


def test_cosine_orthogonal_vectors():
    """Test cosine similarity of orthogonal vectors"""
    v1 = np.array([1.0, 0.0], dtype="float32")
    v2 = np.array([0.0, 1.0], dtype="float32")
    similarity = _cosine(v1, v2)
    assert abs(similarity) < 1e-6  # Should be ~0


def test_cosine_opposite_vectors():
    """Test cosine similarity of opposite vectors"""
    v1 = np.ones(128, dtype="float32")
    v2 = -np.ones(128, dtype="float32")
    similarity = _cosine(v1, v2)
    assert abs(similarity - (-1.0)) < 1e-6  # Should be -1


def test_cosine_range():
    """Test that cosine similarity is in valid range"""
    v1 = _mock_embedding(128)
    v2 = _mock_embedding(128)
    similarity = _cosine(v1, v2)
    assert -1.0 <= similarity <= 1.0
