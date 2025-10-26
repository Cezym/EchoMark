import secrets

import numpy as np


def generate_watermark(length: int) -> str:
    if length % 8 != 0:
        raise ValueError("Długość watermarku musi być wielokrotnością 8 bitów")
    num_bytes = length // 8
    return secrets.token_hex(num_bytes)


def embed_echo(
    audio: np.ndarray,
    alpha: float,
    delta: int,
    watermark: str | None = None,
) -> np.ndarray:
    print(np.max(audio))
    bipolar = watermark_to_bipolar(watermark) if watermark else None
    return add_echo(audio, alpha, delta, bipolar)


def watermark_to_bipolar(watermark: str) -> np.ndarray:
    watermark_bytes = bytes.fromhex(watermark)
    bits = np.unpackbits(np.frombuffer(watermark_bytes, dtype=np.uint8))
    p_bipolar = 2 * bits - 1
    return p_bipolar


def add_echo(
    data: np.ndarray, alpha: float, delta: int, pattern: np.ndarray | None = None
) -> np.ndarray:
    if delta <= 0 or alpha == 0:
        return data

    x = np.copy(data).astype(np.float32)
    if x.ndim == 1:
        x = x[:, None]
    n, C = x.shape
    y = np.copy(x)
    if delta >= n:
        return y.squeeze()
    if pattern is None:
        y[delta:] += alpha * x[:-delta]
    else:
        pattern = np.asarray(pattern, dtype=np.float32)
        for i in range(min(len(pattern), n - delta)):
            y[delta + i, :] += alpha * pattern[i] * x[i, :]
    max_val = np.max(np.abs(y))
    if max_val > 1.0:
        y = y / max_val

    return y.squeeze()
