import hypothesis.extra.numpy as hynp
import numpy as np
from hypothesis import given
from hypothesis import strategies as st

from src.logic.utils import normalize_audio

BIG_ATOL = 1e-6
SMALL_ATOL = 1e-6
MIN_INT = -32768
MAX_INT = 32767


def test_stereo_normalization():
    """
    Verify that ``normalize_audio`` correctly normalizes a stereo signal.

    The input is a 2‑channel (stereo) array of type ``int16``.
    normalization divides every sample by the maximum absolute value found in the
    original data plus a small tolerance (`SMALL_ATOL`) to avoid division by zero.

    The test checks:
        * Each output sample equals the expected value computed as
          ``audio.astype(np.float32) / (max_val + SMALL_ATOL)``.
        * The returned array has the same shape as the input.
    """

    audio = np.array([[1, 100], [2, 200], [3, 300]], dtype=np.int16)
    normalized = normalize_audio(audio)

    max_val = np.max(np.abs(audio))
    expected = audio.astype(np.float32) / (max_val + SMALL_ATOL)

    assert np.allclose(normalized, expected, atol=BIG_ATOL)
    assert normalized.shape == audio.shape


int16_array_strategy = hynp.arrays(
    dtype=np.int16,
    shape=st.tuples(st.integers(1, 20), st.integers(1, 20)),
    elements=st.integers(MIN_INT, MAX_INT),
)


@given(audio=int16_array_strategy)
def test_mono_normalization_property(audio):
    """
    Property‑based test for mono (single‑channel) normalization.

    * The output from ``normalize_audio`` is a float32 array.
    * If the input contains at least one non‑zero sample, the maximum absolute value
      of the normalized data must be within ``BIG_ATOL`` of 1.0.
    * The shape of the output matches the input shape.

    This test uses Hypothesis to generate many random audio buffers,
    ensuring that edge cases (large values, negative values, etc.) are exercised.

    Parameters
    ----------
    audio : np.ndarray[int16]
        Randomly generated 1‑D or 2‑D array of int16 samples.
    """

    normalized = normalize_audio(audio)

    # Jeśli sygnał jest zerowy – maksymalna wartość to 0, więc nie musimy sprawdzać np.isclose
    if not np.all(audio == 0):
        assert np.isclose(
            np.max(np.abs(normalized)), 1.0, atol=BIG_ATOL
        ), "Max absolute value after normalization is not close to 1"

    assert normalized.dtype == np.float32, f"Expected float32, got {normalized.dtype}"
    assert normalized.shape == audio.shape, "Shape changed during normalization"


@given(audio=int16_array_strategy)
def test_zero_signal_property(audio):
    """
    Property‑based test for the special case where the input signal is all zeros.

    * normalizing an all‑zero signal must return an array of zeros (float32).
    * The result must contain no NaNs or infinities.
    * The shape of the output matches the input shape.

    This guarantees that the normalization routine gracefully handles silent audio.

    Parameters
    ----------
    audio : np.ndarray[int16]
        Randomly generated int16 array; it will be overwritten with a zero buffer.
    """

    audio = np.zeros_like(audio, dtype=np.int16)

    normalized = normalize_audio(audio)

    assert np.all(normalized == 0), "Normalized zero signal is not all zeros"
    assert not np.any(np.isnan(normalized)), "NaN found in normalized output"
    assert not np.any(np.isinf(normalized)), "Inf found in normalized output"
    assert normalized.shape == audio.shape, "Shape changed for zero signal"


@given(audio=int16_array_strategy)
def test_dtype_float32_property(audio):
    """
    Property‑based test to ensure type consistency after normalization.

    * The output of ``normalize_audio`` must always be a NumPy array with dtype
      ``np.float32``.
    * The dimensionality (shape) of the output is identical to that of the input.

    This test confirms that no unexpected type promotion occurs during processing.

    Parameters
    ----------
    audio : np.ndarray[int16]
        Randomly generated int16 array (mono or stereo).
    """

    normalized = normalize_audio(audio)

    assert (
        normalized.dtype == np.float32
    ), f"Expected dtype float32, got {normalized.dtype}"
    assert normalized.shape == audio.shape, "Shape changed during normalization"
