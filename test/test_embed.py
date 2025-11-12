import hypothesis.extra.numpy as hynp
import numpy as np
from hypothesis import given
from hypothesis import strategies as st

from src.logic.embed import add_echo

DEFAULT_ATOL = 1e-7
MIN_FLOAT = -32768.0
MAX_FLOAT = 32767.0


@given(
    data=hynp.arrays(
        dtype=np.float32,
        shape=st.tuples(
            st.integers(min_value=2, max_value=20),
            st.integers(min_value=2, max_value=20),
        ),
        elements=st.floats(MIN_FLOAT, MAX_FLOAT),
    ),
    alpha=st.floats(0.0, 1.0),
    delta=st.integers(min_value=1, max_value=100),
)
def test_shape_is_preserved(data: np.ndarray, alpha: float, delta: int):
    """
    Verify that ``add_echo`` does not change the shape of its input.

    The function is called with a 2‑D array whose dimensions are
    independently bounded between 2 and 20. A random echo strength
    (`alpha`) in the range [0, 1] and a delay (`delta`) in samples
    between 1 and 100 are supplied by Hypothesis.

    Parameters
    ----------
    data : np.ndarray
        Arbitrary‑sized 2‑D array of ``np.float32`` values.
    alpha : float
        Echo attenuation factor (0 ≤ α ≤ 1).
    delta : int
        Delay in samples (1 ≤ δ ≤ 100).

    Raises
    ------
    AssertionError
        If the shape of the returned array differs from ``data.shape``.
    """

    out = add_echo(data, alpha=alpha, delta=delta)
    assert out.shape == data.shape


@given(
    data=hynp.arrays(
        dtype=np.float32,
        shape=st.tuples(
            st.integers(min_value=2, max_value=20),
            st.integers(min_value=2, max_value=20),
        ),
        elements=st.floats(MIN_FLOAT, MAX_FLOAT, allow_nan=False, allow_infinity=False),
    ),
    delta=st.integers(min_value=1, max_value=100),
)
def test_no_change_with_zero_alpha(data: np.ndarray, delta: int):
    """
    Confirm that a zero echo strength leaves the input untouched.

    When ``alpha`` is exactly 0.0 no attenuation or addition of delayed
    samples should occur; the output must be byte‑wise identical to the
    input array.

    Parameters
    ----------
    data : np.ndarray
        2‑D array of ``np.float32`` values without NaNs or infinities.
    delta : int
        Delay in samples (1 ≤δ≤100).

    Raises
    ------
    AssertionError
        If the output differs from the original input.
    """

    out = add_echo(data, alpha=0.0, delta=delta)
    np.testing.assert_array_equal(out, data)


def test_simple_echo_stereo():
    """
    Test a minimal stereo echo with a fixed delay and attenuation.

    The input contains two channels; only the second frame receives
    an echo from the first due to ``delta == 2``. The expected output
    demonstrates that the echo is correctly applied per channel.

    Raises
    ------
    AssertionError
        If the computed array does not match the reference within the
        default tolerance defined by ``DEFAULT_ATOL``.
    """

    data = np.array(
        [
            [1.0, -1.0],
            [0.5, -0.5],
            [0.0, 0.0],
            [0.0, 0.0],
        ],
        dtype=np.float32,
    )

    alpha = 0.5
    delta = 2
    out = add_echo(data, alpha, delta)

    expected = np.array(
        [
            [1.0, -1.0],
            [0.5, -0.5],
            [0.5, -0.5],
            [0.25, -0.25],
        ],
        dtype=np.float32,
    )
    np.testing.assert_allclose(out, expected, atol=DEFAULT_ATOL)


def no_echo_if_delta_too_large_strategy():
    """
    Hypothesis strategy that generates test cases where the delay is
    longer than any possible echo path.

    The function draws a random 2‑D array and chooses ``delta`` to be at
    least as large as the longest dimension of the array. In such
    scenarios, ``add_echo`` should simply return the original data.
    """

    @st.composite
    def _inner(draw):
        data = draw(
            hynp.arrays(
                dtype=np.float32,
                shape=st.tuples(st.integers(2, 20), st.integers(2, 20)),
                elements=st.floats(
                    min_value=-1000.0,
                    max_value=1000.0,
                    allow_nan=False,
                    allow_infinity=False,
                ),
            )
        )

        alpha = draw(st.floats(0.0, 1.0))
        min_delta = max(data.shape)
        delta = draw(st.integers(min_delta, min_delta + 100))

        return data, alpha, delta

    return _inner()


@given(strategy=no_echo_if_delta_too_large_strategy())
def test_no_echo_if_delta_too_large(strategy):
    """
    Validate that a delay exceeding the signal length yields no echo.

    Parameters
    ----------
    strategy : tuple
        A Hypothesis generated triple (data, alpha, delta) where
        ``delta`` is guaranteed to be too large for any echo effect.
    """

    data, alpha, delta = strategy
    out = add_echo(data, alpha=alpha, delta=delta)
    np.testing.assert_array_equal(out, data)


def shape_is_preserved_with_pattern_strategy():
    """
    Strategy that creates a random pattern and ensures the output shape
    remains unchanged when this pattern is used.

    The generated ``pattern`` may be smaller than or equal to the input
    dimensions. ``delta`` is drawn from 1 to 100, and ``alpha`` spans
    [0,1].
    """

    @st.composite
    def _inner(draw):
        data = draw(
            hynp.arrays(
                dtype=np.float32,
                shape=st.tuples(st.integers(2, 20), st.integers(2, 20)),
                elements=st.floats(
                    min_value=-1000.0,
                    max_value=1000.0,
                    allow_nan=False,
                    allow_infinity=False,
                ),
            )
        )

        rows, cols = data.shape

        pattern_shape = draw(st.tuples(st.integers(1, rows), st.integers(1, cols)))

        pattern = draw(
            hynp.arrays(
                dtype=np.float32,
                shape=pattern_shape,
                elements=st.floats(
                    min_value=-1000.0,
                    max_value=1000.0,
                    allow_nan=False,
                    allow_infinity=False,
                ),
            )
        )

        alpha = draw(st.floats(0.0, 1.0))
        delta = draw(st.integers(1, 100))

        return data, pattern, alpha, delta

    return _inner()


@given(strategy=shape_is_preserved_with_pattern_strategy())
def test_shape_is_preserved_with_pattern(strategy):
    """
    Ensure that providing a custom echo pattern does not alter the
    dimensionality of the output.

    Parameters
    ----------
    strategy : tuple
        Hypothesis‑generated (data, pattern, alpha, delta) where
        ``pattern`` can be any 2‑D array smaller than or equal to
        ``data``.
    """

    data, pattern, alpha, delta = strategy
    out = add_echo(data, alpha=alpha, delta=delta, pattern=pattern)
    assert out.shape == data.shape


def test_time_spread_mono_simple():
    """Test a mono echo with an explicit time‑spread pattern."""

    data = np.array([0.5, -0.5, 0.0, 0.0], dtype=np.float32)
    pattern = np.array([1, -1], dtype=np.float32)
    alpha = 0.5
    delta = 1

    out = add_echo(data, alpha, delta, pattern)

    expected = np.array([0.5, -0.25, 0.25, 0.0], dtype=np.float32)
    np.testing.assert_allclose(out, expected, atol=DEFAULT_ATOL)


def test_time_spread_stereo_simple():
    """Test a stereo echo with an explicit time‑spread pattern."""

    data = np.array(
        [
            [0.5, -0.5],
            [0.0, 0.0],
            [-0.5, 0.5],
            [0.0, 0.0],
        ],
        dtype=np.float32,
    )
    pattern = np.array([1, -1], dtype=np.float32)
    alpha = 0.5
    delta = 1

    out = add_echo(data, alpha, delta, pattern)

    expected = np.array(
        [
            [0.5, -0.5],
            [0.25, -0.25],
            [-0.5, 0.5],
            [0.0, 0.0],
        ],
        dtype=np.float32,
    )
    np.testing.assert_allclose(out, expected, atol=DEFAULT_ATOL)


def time_spread_too_large_delta_strategy():
    """
    Strategy for testing that a pattern longer than the signal length
    is ignored.

    ``delta`` is chosen to be at least as large as the maximum input
    dimension, ensuring no part of the pattern can contribute an echo.
    """

    @st.composite
    def _inner(draw):
        data = draw(
            hynp.arrays(
                dtype=np.float32,
                shape=st.tuples(st.integers(2, 20), st.integers(2, 20)),
                elements=st.floats(
                    min_value=-1000.0,
                    max_value=1000.0,
                    allow_nan=False,
                    allow_infinity=False,
                ),
            )
        )

        rows, cols = data.shape

        pattern_shape = draw(st.tuples(st.integers(1, rows), st.integers(1, cols)))

        pattern = draw(
            hynp.arrays(
                dtype=np.float32,
                shape=pattern_shape,
                elements=st.floats(
                    min_value=-1000.0,
                    max_value=1000.0,
                    allow_nan=False,
                    allow_infinity=False,
                ),
            )
        )

        alpha = draw(st.floats(0.0, 1.0))

        min_delta = max(data.shape)
        delta = draw(st.integers(min_delta, min_delta + 100))

        return data, pattern, alpha, delta

    return _inner()


@given(strategy=time_spread_too_large_delta_strategy())
def test_time_spread_too_large_delta(strategy):
    """
    Confirm that when the delay is too large for any echo to occur,
    the output equals the input regardless of a supplied pattern.
    """

    data, pattern, alpha, delta = strategy
    out = add_echo(data, alpha=alpha, delta=delta, pattern=pattern)
    np.testing.assert_array_equal(out, data)


def test_time_spread_long_pattern_truncated():
    """Verify that a pattern longer than the input is truncated."""

    data = np.array([0.5, -0.5, 0.0, 0.0], dtype=np.float32)
    pattern = np.array([1, -1, 1, -1, 1, -1], dtype=np.float32)
    alpha = 0.5
    delta = 2

    out = add_echo(data, alpha, delta, pattern)

    expected = np.array([0.5, -0.5, 0.25, 0.25], dtype=np.float32)
    np.testing.assert_allclose(out, expected, atol=DEFAULT_ATOL)
