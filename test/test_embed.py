import numpy as np

from src.logic.embed import add_echo


def test_shape_is_preserved():
    data = np.zeros((6, 2), dtype=np.float32)
    out = add_echo(data, alpha=0.5, delta=2)
    assert out.shape == data.shape


def test_no_change_with_zero_alpha():
    data = np.array(
        [
            [1.0, -1.0],
            [0.5, -0.5],
            [0.0, 0.0],
            [-0.5, 0.5],
        ],
        dtype=np.float32,
    )
    out = add_echo(data, alpha=0.0, delta=2)
    np.testing.assert_array_equal(out, data)


def test_simple_echo_mono():
    data = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32)
    alpha = 0.5
    delta = 2
    out = add_echo(data, alpha, delta)

    expected = np.array([1.0, 0.0, 0.5, 0.0], dtype=np.float32)
    np.testing.assert_allclose(out, expected, atol=1e-7)


def test_simple_echo_stereo():
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
    np.testing.assert_allclose(out, expected, atol=1e-7)


def test_no_echo_if_delta_too_large():
    data = np.array(
        [
            [1.0, -1.0],
            [0.5, -0.5],
            [0.0, 0.0],
        ],
        dtype=np.float32,
    )
    out = add_echo(data, alpha=0.5, delta=10)
    np.testing.assert_array_equal(out, data)


def test_shape_is_preserved_with_pattern():
    data = np.zeros((6, 2), dtype=np.float32)
    pattern = np.array([1, -1, 1, -1], dtype=np.float32)
    out = add_echo(data, alpha=0.5, delta=2, pattern=pattern)
    assert out.shape == data.shape


def test_time_spread_mono_simple():
    data = np.array([0.5, -0.5, 0.0, 0.0], dtype=np.float32)
    pattern = np.array([1, -1], dtype=np.float32)
    alpha = 0.5
    delta = 1

    out = add_echo(data, alpha, delta, pattern)

    expected = np.array([0.5, -0.5 + 0.25, 0.0 + 0.25, 0.0], dtype=np.float32)
    np.testing.assert_allclose(out, expected, atol=1e-7)


def test_time_spread_stereo_simple():
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
            [0.0 + 0.25, 0.0 - 0.25],
            [-0.5, 0.5],
            [0.0, 0.0],
        ],
        dtype=np.float32,
    )
    np.testing.assert_allclose(out, expected, atol=1e-7)


def test_time_spread_too_large_delta():
    data = np.array([-0.5, 0.5, 0.0], dtype=np.float32)
    pattern = np.array([1, -1, 1], dtype=np.float32)
    out = add_echo(data, alpha=0.5, delta=10, pattern=pattern)
    np.testing.assert_array_equal(out, data)


def test_time_spread_long_pattern_truncated():
    data = np.array([0.5, -0.5, 0.0, 0.0], dtype=np.float32)
    pattern = np.array([1, -1, 1, -1, 1, -1], dtype=np.float32)
    alpha = 0.5
    delta = 2

    out = add_echo(data, alpha, delta, pattern)

    expected = np.array([0.5, -0.5, 0.25, 0.25], dtype=np.float32)

    np.testing.assert_allclose(out, expected, atol=1e-7)
