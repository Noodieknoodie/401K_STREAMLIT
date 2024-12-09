"""Session state management utilities."""
import streamlit as st
from shared.constants.app_config import PAGE_TITLES, DEFAULT_PAGE

def initialize_session_state():
    """Initialize or reset the session state with default values."""
    if 'current_page' not in st.session_state:
        st.session_state.current_page = PAGE_TITLES[DEFAULT_PAGE]
    if 'selected_client' not in st.session_state:
        st.session_state.selected_client = None

def get_current_page():
    """Get the current page from session state."""
    return st.session_state.get('current_page', PAGE_TITLES[DEFAULT_PAGE])

def set_current_page(page_key):
    """Set the current page in session state."""
    st.session_state.current_page = PAGE_TITLES[page_key]

def get_selected_client():
    """Get the selected client from session state."""
    return st.session_state.get('selected_client')

def set_selected_client(client_id):
    """Set the selected client in session state."""
    st.session_state.selected_client = client_id 