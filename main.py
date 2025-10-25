import io

import librosa
import numpy as np
import streamlit as st
from pydub import AudioSegment

import pipelines.EchoMark.features

# Lista utworór pokazana po wywołaniu librosa.util.files.list_examples()
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
    audio, sr = librosa.load(librosa.example(audio_name, hq=True), sr=None, mono=True)

st.write(f"Sample rate: {sr} Hz, Audio shape: {audio.shape}")
audio_int16 = np.int16(audio * 32767)
audio_segment = AudioSegment(audio_int16.tobytes(), frame_rate=sr, sample_width=audio_int16.dtype.itemsize, channels=1)
buffer = io.BytesIO()
audio_segment.export(buffer, format="mp3")
buffer.seek(0)
st.audio(buffer, format="audio/mp3")

standard_cepstrum = pipelines.EchoMark.features.cepstrum(audio)[:200]

st.line_chart(standard_cepstrum)

# Inicjalizacja stanu sesji
if 'num_boxes' not in st.session_state:
    st.session_state.num_boxes = 0
if 'sliders' not in st.session_state:
    st.session_state.sliders = {}
if 'box_ids' not in st.session_state:
    st.session_state.box_ids = []

# Przycisk do dodawania echa
if st.button("Dodaj nowe echo"):
    st.session_state.num_boxes += 1
    new_id = st.session_state.num_boxes
    st.session_state.box_ids.append(new_id)
    st.session_state.sliders[new_id] = [0.0, 0]

# Wyświetlanie okienek z suwakami
for box_id in st.session_state.box_ids[:]:  # Kopia listy, aby uniknąć błędów przy usuwaniu
    with st.expander(f"Echo {box_id}"):
        alpha = st.slider(f"Alpha", min_value=0.01, max_value=1.0, value=st.session_state.sliders[box_id][0],
                          key=f"alpha_{box_id}")
        delta = st.slider(f"Delta", min_value=25, max_value=100, value=st.session_state.sliders[box_id][1],
                          key=f"delta_{box_id}")
        st.session_state.sliders[box_id] = [alpha, delta]

        # Przycisk "Usuń"
        if st.button("Usuń echo", key=f"delete_{box_id}"):
            st.session_state.box_ids.remove(box_id)
            del st.session_state.sliders[box_id]

echo_audio = audio
for value in st.session_state.sliders.values():
    alpha, delta = value[0], value[1]
    echo_audio = pipelines.EchoMark.features.add_echo_to_audio(data=echo_audio, alpha=alpha, delta=delta,
                                                               generate_keys=False)

echo_cepstrum = pipelines.EchoMark.features.cepstrum(echo_audio)[:200]
st.line_chart(echo_cepstrum)

echo_audio_int16 = np.int16(echo_audio * 32767)
echo_audio_segment = AudioSegment(echo_audio_int16.tobytes(), frame_rate=sr, sample_width=echo_audio_int16.dtype.itemsize, channels=1)
buffer_echo = io.BytesIO()
echo_audio_segment.export(buffer_echo, format="mp3")
buffer_echo.seek(0)
st.audio(buffer_echo, format="audio/mp3")
