import streamlit as st

from ui.tabs.detect_tab import DetectTab
from ui.tabs.embed_tab import EmbedTab
from ui.tabs.experiments_tab import ExperimentsTab
from ui.tabs.librosa_tab import LibrosaTab
from ui.tabs.help_tab import HelpTab


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
