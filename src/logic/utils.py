from io import BytesIO

import numpy as np
from numpy import log, abs
from numpy.fft import ifft, fft
from pydub import AudioSegment

LOG_FLOOR = 0.00001


def cepstrum(data: np.ndarray) -> np.ndarray:
    return ifft(log(abs(fft(data)) ** 2 + LOG_FLOOR)).real


def normalize_audio(audio: np.ndarray) -> np.ndarray:
    audio = audio.astype(np.float32)
    max_val = np.max(np.abs(audio)) + 1e-12
    return audio / max_val


def audio_to_mp3_buffer(audio: np.ndarray, sr: int) -> BytesIO:
    audio_int16 = np.int16(audio * 32767)
    segment = AudioSegment(
        audio_int16.tobytes(),
        frame_rate=sr,
        sample_width=audio_int16.dtype.itemsize,
        channels=1,
    )
    buffer = BytesIO()
    segment.export(buffer, format="mp3")
    buffer.seek(0)
    return buffer
