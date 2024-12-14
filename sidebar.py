import streamlit as st
from streamlit_extras.button_selector import button_selector
from utils.debug_logger import debug

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

        # Log the current page before navigation
        previous_page = st.session_state.current_page if 'current_page' in st.session_state else nav_options[0]
        
        # Use button_selector for navigation and get the selected index
        selected_index = button_selector(
            nav_options,
            index=nav_options.index(previous_page),
            spec=1,  # Vertical alignment for buttons
            key="sidebar_selector",
            label="Select a page:"
        )

        # Get the newly selected page
        new_page = nav_options[selected_index]
        
        # Only log if there's actually a page change
        if new_page != previous_page:
            debug.log_ui_interaction(
                action="navigation",
                element="sidebar",
                data={
                    "from_page": previous_page,
                    "to_page": new_page
                }
            )
        
        # Update session state with the selected page
        st.session_state.current_page = new_page
