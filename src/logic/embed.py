import secrets
import numpy as np
from matplotlib import pyplot as plt


LOG_FLOOR = 0.00001


def add_echo_to_audio(*, data, alpha, delta, generate_keys=False, seed=None):
    """Dodaje echo do sygnału audio.

    Kopiuje sygnał i dodaje echo do każdego kanału (mono lub stereo) według formuły: x[n] + alpha * x[n - delta].
    Obsługuje sygnały mono i stereo. Nie normalizuje sygnału.

    Args:
        data (numpy.ndarray): Sygnał audio, tablica 1D (mono) lub 2D (stereo, shape: [próbki, kanały]).
        alpha (float): Siła echa (np. 0.4 dla umiarkowanego echa).
        delta (int): Opóźnienie echa w próbkach (np. 100 dla ~2.3 ms przy 44.1 kHz).

    Returns:
        numpy.ndarray: Sygnał z dodanym echem, ten sam kształt co wejściowy.

    Raises:
        ValueError: Gdy data jest pusta lub delta jest ujemne/zero.
        TypeError: Gdy data nie jest tablicą numpy.ndarray.

    Example:
        >>> import numpy as np
        >>> signal = np.zeros(1000)  # Mono, 1000 próbek
        >>> signal[0] = 1.0
        >>> echoed = add_echo_to_audio(signal, alpha=0.4, delta=100)
        >>> print(echoed[100])  # Powinno być 0.4
    """
    keys = []
    if generate_keys == True:
        if seed is None:
            seed = np.random.randint(0, 1000000)  # Losowy seed
        np.random.seed(seed)
        for _ in range(len(data)):
            keys.append(np.random.randint(2))
        print(np.array(keys))

    # Sygnał wejściowy
    output = np.copy(data)

    if len(data.shape) > 1:
        # Dodaj echo do każdego kanału: x[n] + alpha * x[n - delta]
        for channel in range(data.shape[1]):  # Iteruj po kanałach (0: lewy, 1: prawy)
            for i in range(delta, len(data)):
                if generate_keys == True:
                    output[i, channel] += alpha * data[i - delta, channel] * keys[i]
                else:
                    output[i, channel] += alpha * data[i - delta, channel]

    else:
        # Dodaj echo do kanału
        for i in range(delta, len(data)):
            output[i] += alpha * data[i - delta]

    return output


def cepstrum(data):
    log_floor = LOG_FLOOR

    # Oblicz cepstrum
    cepstrum = np.fft.ifft(np.log(np.abs(np.fft.fft(data)) ** 2 + log_floor)).real

    return cepstrum


def generate_watermark(length: int = 1024) -> str:
    """
    Generuje losowy watermark o zadanej długości w bitach i zwraca go jako HEX.
    1024 bity = 128 bajtów = 256 znaków hex.
    """
    if length % 8 != 0:
        raise ValueError("Długość watermarku musi być wielokrotnością 8 bitów")
    num_bytes = length // 8
    return secrets.token_hex(num_bytes)


def embed_watermark(audio: np.ndarray, watermark: str, alpha: float, delta: int) -> np.ndarray:
    """
    Osadza watermark w audio metodą time-spread echo.

    :param audio: sygnał audio jako 1D numpy array (float32, znormalizowany do [-1,1])
    :param watermark: ciąg hex zawierający watermark (np. 256 znaków dla 1024 bitów)
    :param alpha: współczynnik siły echa (0.005–0.02 zalecane)
    :param delta: bazowe opóźnienie echa (np. 75 próbek)
    :return: nowy sygnał audio z osadzonym watermarkiem
    """
    # --- walidacja wejścia ---
    if not isinstance(audio, np.ndarray):
        raise TypeError("audio musi być numpy.ndarray")
    if audio.ndim != 1:
        raise ValueError("audio musi być jednowymiarową tablicą (mono)")
    if len(watermark) % 2 != 0:
        raise ValueError("watermark musi mieć parzystą liczbę znaków HEX")

    # --- konwersja watermarku HEX -> bity -> -1/+1 ---
    watermark_bytes = bytes.fromhex(watermark)
    bits = np.unpackbits(np.frombuffer(watermark_bytes, dtype=np.uint8))
    p_bipolar = 2 * bits - 1  # 0 → -1, 1 → +1

    # --- osadzanie echa ---
    y = np.copy(audio).astype(np.float32)
    L = len(p_bipolar)
    N = len(y)

    for i in range(L):
        shift = delta + i
        if shift < N:
            y[shift:] += alpha * p_bipolar[i] * audio[:-shift]

    # --- normalizacja po watermarkingu ---
    y = y / (np.max(np.abs(y)) + 1e-12)
    return y