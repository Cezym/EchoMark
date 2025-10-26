import numpy as np
from scipy.fft import fft, ifft


def detect_watermark(
    audio: np.ndarray,
    rate: int,
    method: str = "time-spread",
    expected_watermark_hex: str = None,
    search_range: tuple = (20, 500),
    sigma_factor: float = 4.0,
    snr_threshold: float = 5.0,
    local_ratio: float = 2.0,
) -> dict:
    """
    Detects simple echo or time-spread watermark in audio with improved reliability.

    :param audio: 1D numpy array (float32, mono, normalized)
    :param rate: sample rate of the audio
    :param method: "simple" or "time-spread"
    :param expected_watermark_hex: required if method="time-spread"
    :param search_range: tuple (start, end) for cepstrum peak search (samples)
    :param sigma_factor: how many std dev above mean is considered a detection
    :param snr_threshold: minimum peak-to-mean ratio for detection
    :param local_ratio: how many times higher than local neighborhood peak must be
    :return: dict with detection info
    """
    if audio.ndim != 1:
        raise ValueError("Audio must be mono (1D numpy array).")

    # --- Compute cepstrum ---
    spectrum = fft(audio)
    cepstrum = np.real(ifft(np.log(np.abs(spectrum) + 1e-10)))

    result = {"method": method, "detected": False}

    # ==========================================================
    # SIMPLE ECHO DETECTION
    # ==========================================================
    if method == "simple":
        start, end = search_range
        segment = cepstrum[start:end]
        if len(segment) == 0:
            result["error"] = "Cepstrum segment is empty."
            return result

        peak_idx = np.argmax(segment) + start
        peak_val = cepstrum[peak_idx]

        mu = np.mean(segment)
        sigma = np.std(segment)
        threshold = mu + sigma_factor * sigma
        snr_ratio = peak_val / (np.mean(np.abs(segment)) + 1e-12)

        detected = peak_val > threshold and snr_ratio > snr_threshold

        result.update(
            {
                "peak_index": int(peak_idx),
                "peak_time_s": float(peak_idx / rate),
                "peak_value": float(peak_val),
                "threshold": float(threshold),
                "snr_ratio": float(snr_ratio),
                "detected": detected,
            }
        )

    # ==========================================================
    # TIME-SPREAD WATERMARK DETECTION
    # ==========================================================
    elif method == "time-spread":
        if expected_watermark_hex is None:
            raise ValueError(
                "expected_watermark_hex is required for time-spread detection."
            )

        watermark_bytes = bytes.fromhex(expected_watermark_hex)
        bits = np.unpackbits(np.frombuffer(watermark_bytes, dtype=np.uint8))
        p_bipolar = 2 * bits - 1

        corr = np.correlate(cepstrum, p_bipolar, mode="valid")
        if len(corr) == 0:
            result["error"] = "Correlation signal is empty."
            return result

        peak_idx = np.argmax(corr)
        peak_val = corr[peak_idx]

        mu = np.mean(corr)
        sigma = np.std(corr)
        threshold = mu + sigma_factor * sigma
        snr_ratio = peak_val / (np.mean(np.abs(corr)) + 1e-12)

        # --- Safe local max calculation ---
        win = 50
        left = max(0, peak_idx - win)
        right = min(len(corr), peak_idx + win)

        left_max = np.max(corr[left:peak_idx]) if peak_idx > left else 0
        right_max = np.max(corr[peak_idx + 1 : right]) if right > peak_idx + 1 else 0
        local_max = max(left_max, right_max)

        detected = (
            peak_val > threshold
            and snr_ratio > snr_threshold
            and peak_val > local_ratio * local_max
        )

        result.update(
            {
                "peak_index": int(peak_idx),
                "peak_time_s": float(peak_idx / rate),
                "peak_value": float(peak_val),
                "threshold": float(threshold),
                "snr_ratio": float(snr_ratio),
                "local_max": float(local_max),
                "detected": detected,
                "correlation_signal": corr,
            }
        )

    else:
        raise ValueError("method must be 'simple' or 'time-spread'.")

    return result
