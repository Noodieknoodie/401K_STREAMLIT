# app.py
import streamlit as st
from sidebar import render_sidebar
from pages.quarterly_summary.summary import show_quarterly_summary
from pages.client_dashboard.dashboard import show_client_dashboard
from pages.manage_clients.client_management import show_manage_clients
from pages.bulk_payment.bulk_entry import show_bulk_payment_entry
from shared.constants.app_config import (
    APP_TITLE, PAGE_ICON, PAGE_LAYOUT, 
    SIDEBAR_STATE, PAGE_TITLES
)
from shared.state.session import initialize_session_state, get_current_page

# Set page config
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=PAGE_ICON,
    layout=PAGE_LAYOUT,
    initial_sidebar_state=SIDEBAR_STATE
)

def main():
    # Initialize session state
    initialize_session_state()

    # Render sidebar
    render_sidebar()

    # Main content area
    current_page = get_current_page()
    if current_page == PAGE_TITLES['quarterly_summary']:
        show_quarterly_summary()
    elif current_page == PAGE_TITLES['client_dashboard']:
        show_client_dashboard()
    elif current_page == PAGE_TITLES['manage_clients']:
        show_manage_clients()
    elif current_page == PAGE_TITLES['bulk_payment']:
        show_bulk_payment_entry()

if __name__ == "__main__":
    main()
