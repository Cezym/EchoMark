import numpy as np

from src.logic.utils import normalize_audio


def test_mono_normalization():
    audio = np.array([0, 2, -4], dtype=np.int16)
    normalized = normalize_audio(audio)

    assert np.isclose(np.max(np.abs(normalized)), 1.0, atol=1e-6)
    assert normalized.dtype == np.float32
    assert normalized.shape == audio.shape


def test_stereo_normalization():
    audio = np.array([[1, 100], [2, 200], [3, 300]], dtype=np.int16)
    normalized = normalize_audio(audio)

    max_val = np.max(np.abs(audio))
    expected = audio.astype(np.float32) / (max_val + 1e-12)

    assert np.allclose(normalized, expected, atol=1e-6)
    assert normalized.shape == audio.shape


def test_zero_signal():
    audio = np.zeros((5, 2), dtype=np.int16)
    normalized = normalize_audio(audio)

    assert np.all(normalized == 0)
    assert not np.any(np.isnan(normalized))
    assert not np.any(np.isinf(normalized))
    assert normalized.shape == audio.shape


def test_dtype_float32():
    audio = np.array([100, -100], dtype=np.int16)
    normalized = normalize_audio(audio)

    assert normalized.dtype == np.float32
    assert normalized.shape == audio.shape
