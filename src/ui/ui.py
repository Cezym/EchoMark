import streamlit as st

from ui.tabs import DetectTab, EmbedTab, ExperimentsTab, HelpTab, LibrosaTab


class UI:
    def __init__(self) -> None:
        st.set_page_config(
            page_title="Echo Watermark",
            page_icon="🎧",
            layout="wide",
        )
        tab_classes = [EmbedTab, DetectTab, ExperimentsTab, LibrosaTab, HelpTab]
        st_tabs = st.tabs([tab.title for tab in tab_classes])

        for st_tab, tab_class in zip(st_tabs, tab_classes):
            with st_tab:
                tab_class()
