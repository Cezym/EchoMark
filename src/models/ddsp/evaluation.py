import numpy as np
import matplotlib.pyplot as plt
import librosa
import soundfile as sf
import os

from .model import DDSPDecoder


def transfer_audio_style(model_path, input_audio, device='cuda', pitch_shift=0, sr=44100, hop_length=441, reverb_len=44100):
    model = DDSPDecoder(mlp_depth=3, n_units=512, n_harmonics=50, n_bands=65,
                        hop_length=hop_length, sr=sr, reverb_len=reverb_len)
    model.load_from_file(model_path)
    model = model.to(device)
    model.eval()
    print("Evaluating...")

    return model.style_transfer(input_audio, device=device, pitch_shift=pitch_shift)


def do_evaluation(model_path, input_audio_path, output_audio_path, device='cuda', pitch_shift=0, sr=44100, hop_length=441, reverb_len=44100 ):
    x, sr = librosa.load(input_audio_path, sr=sr)
    x = x.astype(np.float32)

    y = transfer_audio_style(model_path, x, device, pitch_shift, sr, hop_length, reverb_len)

    # Save synthesised audio
    os.makedirs(os.path.dirname(output_audio_path), exist_ok=True)
    sf.write(output_audio_path, y, sr)

    # Make visual comparison
    plt.figure(figsize=(12, 6))
    plt.subplot(121)
    plt.title("Oryginalne STFT")
    Sx = np.abs(librosa.stft(x))
    librosa.display.specshow(librosa.amplitude_to_db(Sx, amin=1e-10), sr=sr, x_axis='time', y_axis='log')
    plt.colorbar(format='%+2.0f dB')

    plt.subplot(122)
    plt.title("Syntezowane STFT")
    Sy = np.abs(librosa.stft(y))
    librosa.display.specshow(librosa.amplitude_to_db(Sy, amin=1e-10), sr=sr, x_axis='time', y_axis='log')
    plt.colorbar(format='%+2.0f dB')

    plt.tight_layout()
    plt.savefig(output_audio_path.replace('.wav', '_comparison.png'))
    plt.show()

    print(f"Ewaluacja zakończona. Syntezowane audio zapisane w: {output_audio_path}")