import io

import numpy as np
import soundfile as sf
import streamlit as st
from scipy.io import wavfile

from embed import embed_simple_echo, embed_watermark, generate_watermark


class EmbedTab:
    title = "➕ Embed watermark"

    def __init__(self):
        super().__init__()
        if "audio_bytes" not in st.session_state:
            st.session_state.audio_bytes = None
        if "selected_pattern" not in st.session_state:
            st.session_state.selected_pattern = {
                "id": "PATT-001",
                "len": 1024,
                "desc": "Default pseudo-random time-spread",
                "hex": None,
            }
        st.subheader(EmbedTab.title)

        # ==========================================================
        # 1️⃣  UPLOAD AUDIO FILE
        # ==========================================================
        st.markdown("### 📁 Upload Audio File (WAV)")
        audio_file = st.file_uploader("Choose a WAV audio file", type=["wav"], key="embed_audio")
        if audio_file is not None:
            st.session_state.audio_bytes = audio_file.read()
            st.audio(st.session_state.audio_bytes, format="audio/wav")
            st.success("✅ Audio file loaded successfully.")

        # ==========================================================
        # 2️⃣  WATERMARK METHOD SELECTION
        # ==========================================================
        st.markdown("### 🛠️ Choose Watermark Embedding Method")
        method = st.radio(
            "Method:",
            ["Simple Echo", "Time-Spread Echo"],
            help="Simple Echo = 1 bit; Time-Spread Echo = 1024-bit signature",
        )

        alpha = st.slider(
            "Echo strength (alpha)",
            0.001,
            0.5,
            0.01 if method == "Time-Spread Echo" else 0.4,
            step=0.001,
        )
        delta = st.slider("Echo delay (delta, samples)", 10, 300, 75, step=1)

        # ==========================================================
        # 3️⃣  WATERMARK HEX (only for Time-Spread)
        # ==========================================================
        if method == "Time-Spread Echo":
            st.markdown("### 🔐 Watermark Pattern (1024 bits HEX)")
            current_hex = st.session_state.selected_pattern.get("hex", "")
            hex_input = st.text_area(
                "Paste or generate a 1024-bit watermark (256 hex characters)",
                value=current_hex,
                height=100,
            )

            if hex_input:
                hex_input = hex_input.strip()
                if len(hex_input) == 256 and all(c in "0123456789abcdefABCDEF" for c in hex_input):
                    st.session_state.selected_pattern["hex"] = hex_input
                    st.success("✅ Watermark is valid.")
                else:
                    st.error("❌ Watermark must be exactly 256 HEX characters (1024 bits).")

            if st.button("🔄 Generate new watermark"):
                st.session_state.selected_pattern["hex"] = generate_watermark(1024)
                st.rerun()

        # ==========================================================
        # 4️⃣  EMBED WATERMARK INTO AUDIO
        # ==========================================================
        st.markdown("### 📥 Embed Watermark into Audio")
        if st.button("💾 Embed Watermark"):
            if st.session_state.audio_bytes is None:
                st.error("❌ Please upload an audio file first.")
                return

            # --- Read audio into numpy array ---
            with io.BytesIO(st.session_state.audio_bytes) as f:
                rate, audio = wavfile.read(f)
            if audio.ndim > 1:
                audio = audio[:, 0]
            audio = audio.astype(np.float32)
            audio = audio / (np.max(np.abs(audio)) + 1e-12)

            # --- Choose method ---
            if method == "Simple Echo":
                watermarked = embed_simple_echo(audio, alpha=alpha, delta=delta)
            else:
                wm_hex = st.session_state.selected_pattern["hex"]
                if not wm_hex:
                    st.error("❌ Please paste or generate a watermark first.")
                    return
                watermarked = embed_watermark(audio, wm_hex, alpha=alpha, delta=delta)

            # --- Save and offer download ---
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
