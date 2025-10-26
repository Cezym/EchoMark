import io
from enum import StrEnum

import soundfile as sf
import streamlit as st
from scipy.io import wavfile

from logic.embed import embed_echo, generate_watermark
from logic.utils import normalize_audio


class EchoType(StrEnum):
    TIME_SPREAD = "Time-Spread Echo"
    SIMPLE = "Simple Echo"


class EmbedTab:
    title = "➕ Embed watermark"

    def __init__(self):
        super().__init__()
        self.__init_session_state()
        st.subheader(self.title)

        self.__upload_audio_section()
        method, alpha, delta = self.__echo_method_section()
        if method == EchoType.TIME_SPREAD:
            self.__watermark_section()
        self.__embed_audio_section(method, alpha, delta)

    def __init_session_state(self):
        st.session_state.setdefault("audio_bytes", None)
        st.session_state.setdefault("selected_pattern", {"hex": None})

    def __upload_audio_section(self):
        st.markdown("### 📁 Upload Audio File (WAV)")
        audio_file = st.file_uploader(
            "Choose a WAV audio file", type=["wav"], key="embed_audio"
        )

        if audio_file:
            st.session_state.audio_bytes = audio_file.read()
            st.audio(st.session_state.audio_bytes, format="audio/wav")
            st.success("✅ Audio file loaded successfully.")

    def __echo_method_section(self):
        st.markdown("### 🛠️ Choose Watermark Embedding Method")
        method = st.radio("Method:", [EchoType.SIMPLE, EchoType.TIME_SPREAD])

        alpha = st.slider(
            "Echo strength (alpha)",
            0.001,
            0.5,
            0.01 if method == EchoType.TIME_SPREAD else 0.4,
            step=0.001,
        )
        delta = st.slider("Echo delay (delta, samples)", 10, 300, 75, step=1)
        return method, alpha, delta

    def __watermark_section(self):
        st.markdown("### 🔐 Watermark Pattern (1024 bits HEX)")

        current_hex = st.session_state.selected_pattern.get("hex", "")
        hex_input = st.text_area(
            "Paste or generate a 1024-bit watermark (256 hex characters)",
            value=current_hex,
            height=100,
        )

        if hex_input:
            if self.__validate_hex_string(hex_input):
                st.session_state.selected_pattern["hex"] = hex_input
                st.success("✅ Watermark is valid.")
            else:
                st.error("❌ Watermark must be exactly 256 HEX characters (1024 bits).")

        if st.button("🔄 Generate new watermark"):
            st.session_state.selected_pattern["hex"] = generate_watermark(1024)
            st.rerun()

    def __embed_audio_section(self, method, alpha, delta):
        st.markdown("### 📥 Embed Watermark into Audio")

        if st.button("💾 Embed Watermark"):
            if st.session_state.audio_bytes is None:
                st.error("❌ Please upload an audio file first.")
                return

            wm_hex = (
                st.session_state.selected_pattern["hex"]
                if method == EchoType.TIME_SPREAD
                else None
            )
            if method == EchoType.TIME_SPREAD and not wm_hex:
                st.error("❌ Please paste or generate a watermark first.")
                return

            rate, audio = wavfile.read(io.BytesIO(st.session_state.audio_bytes))
            audio = normalize_audio(audio)

            watermarked = embed_echo(audio, alpha, delta, wm_hex)

            out_buffer = io.BytesIO()
            sf.write(out_buffer, watermarked, rate, format="WAV")

            st.markdown("#### Watermarked audio")
            st.audio(out_buffer.getvalue(), format="audio/wav")
            st.download_button(
                "⬇️ Download watermarked audio",
                out_buffer.getvalue(),
                "watermarked.wav",
                "audio/wav",
            )

    @staticmethod
    def __validate_hex_string(value: str) -> bool:
        return len(value) == 256 and all(c in "0123456789abcdefABCDEF" for c in value)
