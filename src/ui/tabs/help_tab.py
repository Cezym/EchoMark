import os

import streamlit as st


class HelpTab:
    title = "❓ Help / About"

    def __init__(self):
        st.subheader(HelpTab.title)
        with open(
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                "..",
                "..",
                "..",
                "README.md",
            )
        ) as f:
            st.markdown(f.read(), unsafe_allow_html=True)
