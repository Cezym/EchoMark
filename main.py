import io

import librosa
import numpy as np
import streamlit as st
from pydub import AudioSegment

import pipelines.EchoMark.features

librosa_list_examples = """brahms          Brahms - Hungarian Dance #5
choice          Admiral Bob - Choice (drum+bass)
fishin          Karissa Hobbs - Let's Go Fishin'
humpback        Glacier Bay 60-second clip humpback whale song November 2020
libri1          Ashiel Mystery - A Detective Story, chapter 2, narrated by Garth Comira
libri2          The Age of Chivalry / Chapter 18: Perceval / Read by Anders Lankford
libri3          Sense and Sensibility / Chapter 18 / Jane Austen / Read by Heather Barnett
nutcracker      Tchaikovsky - Dance of the Sugar Plum Fairy
pistachio       The Piano Lady - Pistachio Ice Cream Ragtime
robin           Bird Whistling, Robin, Single, 13.wav / InspectorJ
sweetwaltz      Setuniman - Sweet Waltz
trumpet         Mihai Sorohan - Trumpet loop
vibeace         Kevin MacLeod - Vibe Ace"""
title_desc = librosa_list_examples.split("\n")
title_desc = {pack.split("  ")[-1]: pack.split("  ")[0] for pack in title_desc}

audio_title = st.radio("Pick example from librosa", title_desc.keys())
audio_name = title_desc[audio_title]
if audio_title is not None:
    audio, sr = librosa.load(librosa.example(audio_name, hq=True), sr=None, mono=False)

st.write(f"Sample rate: {sr} Hz, Audio shape: {audio.shape}")
audio_segment = AudioSegment(audio.tobytes(), frame_rate=sr, sample_width=audio.dtype.itemsize, channels=1)
buffer = io.BytesIO()
audio_segment.export(buffer, format="flac")
buffer.seek(0)
st.audio(buffer, format="audio/flac")

standard_cepstrum = pipelines.EchoMark.features.cepstrum(audio)[:200]

st.line_chart(standard_cepstrum)

alpha = st.slider("Pick alpha", 0.01, 1.0)
delta = st.slider("Pick delta", 25, 100)

echo_audio = pipelines.EchoMark.features.add_echo_to_audio(data=audio, alpha=alpha, delta=delta,
                                                           generate_keys=False)

echo_cepstrum = pipelines.EchoMark.features.cepstrum(echo_audio)[:200]
st.line_chart(echo_cepstrum)

echo_audio_normalised= echo_audio / np.max(np.abs(echo_audio))
echo_audio_segment = AudioSegment(echo_audio_normalised.tobytes(), frame_rate=sr, sample_width=echo_audio_normalised.dtype.itemsize, channels=1)
buffer_echo = io.BytesIO()
audio_segment.export(buffer_echo, format="mp3")
buffer_echo.seek(0)
st.audio(buffer_echo, format="audio/mp3")
