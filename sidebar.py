import streamlit as st
from streamlit_extras.button_selector import button_selector

def render_sidebar():
    """Render the sidebar navigation with full-width buttons using Streamlit Extras."""
    with st.sidebar:
        st.title("401K Payment Tracker")
        st.subheader("Navigation")

        # Navigation options
        nav_options = [
            '📊 Quarterly Summary',
            '👥 Client Dashboard',
            '⚙️ Manage Clients',
            '📝 Bulk Payment Entry'
        ]

        # Use button_selector for navigation and get the selected index
        selected_index = button_selector(
            nav_options,
            index=nav_options.index(st.session_state.current_page) if 'current_page' in st.session_state else 0,
            spec=1,  # Vertical alignment for buttons
            key="sidebar_selector",
            label="Select a page:"
        )

        # Update session state with the selected page
        st.session_state.current_page = nav_options[selected_index]
