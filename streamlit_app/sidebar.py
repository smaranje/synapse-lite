import streamlit as st
import sys
import os

# Add the current directory to the Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import PAGES


def render_sidebar():
    """Render a clean Coinbase Business-style sidebar navigation with working CSS"""

    # Streamlit Sidebar Styling - Hardcoded colors
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {
            background-color: white;
            border-right: 1px solid #E0E0E0;
            min-width: 240px;
            max-width: 240px;
            padding-top: 0;
        }

        [data-testid="stSidebar"] .stRadio > div {
            gap: 0.25rem;
            padding: 0 1rem;
        }

        [data-testid="stSidebar"] .stRadio > div > label {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 0.75rem 1rem;
            margin: 0.125rem 0;
            border-radius: 8px;
            background: transparent;
            color: #444;
            font-weight: 500;
            font-size: 0.875rem;
            cursor: pointer;
            transition: all 0.2s ease;
            border: none;
            width: 100%;
        }

        [data-testid="stSidebar"] .stRadio > div > label:hover {
            background-color: #F6F6F6;
            color: #000;
        }

        [data-testid="stSidebar"] .stRadio > div > label[data-baseweb="radio"] > div:first-child {
            display: none;
        }

        [data-testid="stSidebar"] .stRadio > div > label[aria-checked="true"] {
            background-color: #0052FF;
            color: white;
            font-weight: 600;
        }

        [data-testid="stSidebar"] .stRadio > div > label > div {
            font-size: 0.875rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        # Header / Branding
        st.markdown(
            """
            <div style="padding: 2rem 1rem 1.5rem 1rem; border-bottom: 1px solid #E0E0E0;">
                <div style="display: flex; align-items: center; gap: 0.75rem;">
                    <div style="width: 32px; height: 32px; background: #0052FF; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white; font-weight: 700; font-size: 1rem;">
                        S
                    </div>
                    <div>
                        <div style="font-weight: 600; font-size: 1.1rem; color: #222; line-height: 1.2;">Synapse-Lite</div>
                        <div style="font-size: 0.8rem; color: #777;">Business</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Sidebar Navigation
        page_icons = {
            "Dashboard": "🏠",
            "Transactions": "💳",
            "Analytics": "📊",
            "Alerts": "🔔",
            "Settings": "⚙️",
        }

        page_options = [
            f"{page_icons.get(key, '📄')} {PAGES[key]}"
            for key in PAGES.keys()
        ]

        if "main_nav" not in st.session_state:
            st.session_state.main_nav = page_options[0]

        selected_page_display = st.radio(
            "",
            page_options,
            label_visibility="collapsed",
            index=page_options.index(st.session_state.main_nav),
            key="main_nav",
        )

        # Get actual selected key
        selected_page = None
        for i, (page_key, _) in enumerate(PAGES.items()):
            if page_options[i] == selected_page_display:
                selected_page = page_key
                break

        # Account Info
        st.markdown(
            """
            <div style="position: absolute; bottom: 2rem; left: 1rem; right: 1rem; padding: 1rem; background: #F9F9F9; border-radius: 8px; border: 1px solid #E0E0E0;">
                <div style="display: flex; align-items: center; gap: 0.75rem;">
                    <div style="width: 32px; height: 32px; background: #0052FF; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: 600; font-size: 0.875rem;">
                        LT
                    </div>
                    <div style="flex: 1;">
                        <div style="font-weight: 600; font-size: 0.875rem; color: #222;">Lightray</div>
                        <div style="font-size: 0.75rem; color: #777;">lightray@example.com</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    return selected_page
