import io

import numpy as np
import soundfile as sf
import streamlit as st
from scipy.io import wavfile

from models.ddsp.evaluation import transfer_audio_style


class ModelsTab:
    title = "🇦🇮 Test models"

    def __init__(self):
        super().__init__()
        st.subheader(ModelsTab.title)

        # ==========================================================
        # 1️⃣  UPLOAD AUDIO FILE
        # ==========================================================
        st.markdown("### 📁 Upload Audio File (WAV)")
        audio_file = st.file_uploader("Choose a WAV audio file", type=["wav"], key="model_audio")
        if audio_file is not None:
            st.session_state.audio_bytes = audio_file.read()
            st.audio(st.session_state.audio_bytes, format="audio/wav")
            st.success("✅ Audio file loaded successfully.")

        # ==========================================================
        # 2️⃣  MODEL SELECTION
        # ==========================================================
        st.markdown("### 🛠️ Choose Pretrained Model")
        model = st.radio(
            "Model:",
            ["DDSP", "SAOS"],
            help="Differentiable Digital Signal Processing; Stable Audio Open Small",
        )

        if model == "DDSP":
            pretrained_options = ("Groove", "Guitar")
        elif model == "SAOS":
            pretrained_options = ()
            st.warning("⚠️ SAOS is not implemented yet. Style transfer is disabled for this model.")
        else:
            pretrained_options = ()

        pretrained = st.selectbox(
            "Which style should be your audio?",
            pretrained_options
        )

        model_paths = {
            "DDSP": {
                "Groove": "src/models/ddsp/pretrained_models/groove.pkl",
                "Guitar": "src/models/ddsp/pretrained_models/guitar.pkl",
            }
        }

        if pretrained:
            model_path = model_paths.get(model, {}).get(pretrained)
            if model_path is None:
                st.error("❌ Couldn't find selected style.")
                return
        else:
            return

        # ==========================================================
        # 3️⃣  STYLE TRANSFER INPUT AUDIO
        # ==========================================================
        st.markdown("### 📥 Style Transfer your Audio")
        if st.button("💾 Style Transfer"):
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

            # --- Style transfer ---
            style_transferred = transfer_audio_style(model_path, audio, "cpu", 0, 44100, 441, 44100)

            # --- Save and offer download ---
            out_buffer = io.BytesIO()
            sf.write(out_buffer, style_transferred, rate, format="WAV")

            st.markdown("#### Style transferred audio")
            st.audio(out_buffer.getvalue(), format="audio/wav")
            st.download_button(
                "⬇️ Download style transferred audio",
                out_buffer.getvalue(),
                "style_transferred.wav",
                "audio/wav",
            )
