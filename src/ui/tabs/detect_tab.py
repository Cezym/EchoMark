import io

import numpy as np
import streamlit as st
from scipy.io import wavfile

from detect import detect_watermark


class DetectTab:
    title = "🔍 Detect watermark"

    def __init__(self):
        st.subheader(DetectTab.title)

        # ==========================================================
        # 1️⃣ UPLOAD AUDIO FILE
        # ==========================================================
        st.markdown("### 📁 Upload audio file to analyze (WAV)")
        audio_file = st.file_uploader("Choose a WAV audio file", type=["wav"], key="detect_audio")

        audio = None
        rate = None
        if audio_file is not None:
            bytes_data = audio_file.read()
            with io.BytesIO(bytes_data) as f:
                rate, audio = wavfile.read(f)

            if audio.ndim > 1:
                audio = audio[:, 0]
            audio = audio.astype(np.float32)
            audio = audio / (np.max(np.abs(audio)) + 1e-12)

            st.audio(bytes_data, format="audio/wav")
            st.success("✅ Audio file loaded successfully.")

        # ==========================================================
        # 2️⃣ SELECT DETECTION METHOD
        # ==========================================================
        st.markdown("### 🧠 Select watermark detection method")
        method = st.radio(
            "Method:",
            ["Simple Echo", "Time-Spread Echo"],
            help="Choose how to analyze the audio for embedded watermark.",
        )

        expected_watermark = None
        if method == "Time-Spread Echo":
            expected_watermark = st.text_area(
                "Paste expected 1024-bit watermark HEX (256 hex chars)",
                placeholder="e.g. 3f7a8d... (256 hex chars)",
                height=100,
            )
            if expected_watermark:
                expected_watermark = expected_watermark.strip()

        # ==========================================================
        # 3️⃣ RUN DETECTION
        # ==========================================================
        st.markdown("### 🔍 Detect watermark")
        if st.button("🚀 Run detection"):
            if audio is None:
                st.error("❌ Please upload an audio file first.")
                return

            if method == "Time-Spread Echo" and (not expected_watermark or len(expected_watermark) != 256):
                st.error("❌ Please provide a valid 256-character HEX watermark.")
                return

            # --- call detection ---
            detection_method = "simple" if method == "Simple Echo" else "time-spread"
            result = detect_watermark(
                audio=audio,
                rate=rate,
                method=detection_method,
                expected_watermark_hex=expected_watermark,
            )

            # ==========================================================
            # 4️⃣ DISPLAY RESULTS
            # ==========================================================
            st.markdown("### 📊 Detection Results")
            if result["detected"]:
                st.success("✅ Watermark detected in the audio!")
            else:
                st.warning("⚠️ No watermark detected (or signal is too weak).")

            st.write("**Detection method:**", result["method"])
            st.write("**Peak index:**", result.get("peak_index"))
            st.write("**Peak time (s):**", f"{result.get('peak_time_s', 0):.6f}")
            st.write("**Peak value:**", result.get("peak_value"))

            if result["method"] == "time-spread":
                st.write("**Correlation length:**", len(result.get("correlation_signal", [])))

                # optional plot
                import matplotlib.pyplot as plt

                fig, ax = plt.subplots(figsize=(10, 3))
                ax.plot(result["correlation_signal"])
                ax.set_title("Cepstrum cross-correlation with watermark pattern")
                ax.set_xlabel("Lag (samples)")
                ax.set_ylabel("Correlation amplitude")
                st.pyplot(fig)
