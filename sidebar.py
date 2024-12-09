import streamlit as st
from streamlit_extras.button_selector import button_selector
from shared.constants.app_config import APP_TITLE, PAGE_TITLES
from shared.state.session import get_current_page, set_current_page

def render_sidebar():
    """Render the sidebar navigation with full-width buttons using Streamlit Extras."""
    with st.sidebar:
        st.title(APP_TITLE)
        st.subheader("Navigation")

        # Navigation options - use values from PAGE_TITLES
        nav_options = list(PAGE_TITLES.values())
        current_page = get_current_page()

        # Use button_selector for navigation and get the selected index
        selected_index = button_selector(
            nav_options,
            index=nav_options.index(current_page),
            spec=1,  # Vertical alignment for buttons
            key="sidebar_selector",
            label="Select a page:"
        )

        # Update session state with the selected page
        page_key = list(PAGE_TITLES.keys())[selected_index]
        set_current_page(page_key)
