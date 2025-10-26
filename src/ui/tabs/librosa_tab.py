import librosa
import numpy as np
import streamlit as st

from logic.embed import embed_echo
from logic.utils import cepstrum
from logic.utils import normalize_audio, audio_to_mp3_buffer


class LibrosaTab:
    title = "🧪 Librosa example"

    def __init__(self):
        st.subheader(self.title)
        self.audio, self.sr = self.__audio_selection_section()
        self.__display_original_audio(self.audio, self.sr)
        self.__manage_echo_sliders()
        self.__apply_echoes_and_display_results()

    def __audio_selection_section(self):
        title_desc = {
            "Brahms - Hungarian Dance #5": "brahms",
            "Admiral Bob - Choice (drum+bass)": "choice",
            "Karissa Hobbs - Let's Go Fishin'": "fishin",
            "Glacier Bay 60-second clip humpback whale song November 2020": "humpback",
            "Ashiel Mystery - A Detective Story, chapter 2, narrated by Garth Comira": "libri1",
            "The Age of Chivalry / Chapter 18: Perceval / Read by Anders Lankford": "libri2",
            "Sense and Sensibility / Chapter 18 / Jane Austen / Read by Heather Barnett": "libri3",
            "Tchaikovsky - Dance of the Sugar Plum Fairy": "nutcracker",
            "The Piano Lady - Pistachio Ice Cream Ragtime": "pistachio",
            "Bird Whistling, Robin, Single, 13.wav / InspectorJ": "robin",
            "Setuniman - Sweet Waltz": "sweetwaltz",
            "Mihai Sorohan - Trumpet loop": "trumpet",
            "Kevin MacLeod - Vibe Ace": "vibeace",
        }

        audio_title = st.radio("🎵 Pick example from librosa", title_desc.keys())
        audio_name = title_desc[audio_title]

        audio, sr = librosa.load(
            librosa.example(audio_name, hq=True), sr=None, mono=True
        )
        audio = normalize_audio(audio)
        st.write(f"Sample rate: {sr} Hz | Shape: {audio.shape}")
        return audio, sr

    def __display_original_audio(self, audio: np.ndarray, sr: int):
        buffer = audio_to_mp3_buffer(audio, sr)
        st.audio(buffer, format="audio/mp3")

        st.markdown("#### 🔍 Cepstrum (Original Audio)")
        st.line_chart(cepstrum(audio)[:200])

    def __manage_echo_sliders(self):
        st.session_state.setdefault("num_boxes", 0)
        st.session_state.setdefault("sliders", {})
        st.session_state.setdefault("box_ids", [])

        if st.button("➕ Add new echo"):
            st.session_state.num_boxes += 1
            new_id = st.session_state.num_boxes
            st.session_state.box_ids.append(new_id)
            st.session_state.sliders[new_id] = [0.0, 0]

        for box_id in list(st.session_state.box_ids):
            with st.expander(f"Echo #{box_id}"):
                alpha = st.slider(
                    f"Alpha (strength) #{box_id}",
                    min_value=0.01,
                    max_value=1.0,
                    value=st.session_state.sliders[box_id][0],
                    key=f"alpha_{box_id}",
                )
                delta = st.slider(
                    f"Delta (delay samples) #{box_id}",
                    min_value=25,
                    max_value=100,
                    value=st.session_state.sliders[box_id][1],
                    key=f"delta_{box_id}",
                )
                st.session_state.sliders[box_id] = [alpha, delta]

                if st.button("🗑️ Remove", key=f"delete_{box_id}"):
                    st.session_state.box_ids.remove(box_id)
                    del st.session_state.sliders[box_id]

    def __apply_echoes_and_display_results(self):
        echo_audio = np.copy(self.audio)

        for alpha, delta in st.session_state.sliders.values():
            echo_audio = embed_echo(echo_audio, alpha, delta)

        echo_audio = normalize_audio(echo_audio)

        st.markdown("#### 🔁 Cepstrum (With Echo)")
        st.line_chart(cepstrum(echo_audio)[:200])

        buffer_echo = audio_to_mp3_buffer(echo_audio, self.sr)
        st.audio(buffer_echo, format="audio/mp3")
