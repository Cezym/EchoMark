import streamlit as st


class ExperimentsTab:
    title = "🔬 Experiments"

    def __init__(self):
        st.subheader(ExperimentsTab.title)

        with open("src/ui/tabs/04_sj_ddsp_model.html", "r", encoding="utf-8") as f:
            html_content = f.read()

        st.components.v1.html(html_content, height=1000, scrolling=True)
