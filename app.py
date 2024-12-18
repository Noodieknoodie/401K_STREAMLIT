# app.py
import streamlit as st
from sidebar import render_sidebar
from pages_new.main_summary.summary import show_main_summary
from pages_new.client_dashboard import show_client_dashboard
from pages_new.manage_clients.client_management import show_manage_clients
from pages_new.bulk_payment.bulk_entry import show_bulk_payment_entry

# Set page config
st.set_page_config(
    page_title="401K Payment Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # Initialize session state for navigation
    if 'current_page' not in st.session_state:
        st.session_state.current_page = '📊 Quarterly Summary'  # Ensure it matches the button text
    if 'selected_client' not in st.session_state:
        st.session_state.selected_client = None

    # Render sidebar
    render_sidebar()

    # Main content area
    current_page = st.session_state.current_page
    if current_page == '📊 Quarterly Summary':
        show_main_summary()
    elif current_page == '👥 Client Dashboard':
        show_client_dashboard()
    elif current_page == '⚙️ Manage Clients':
        show_manage_clients()
    elif current_page == '📝 Bulk Payment Entry':
        show_bulk_payment_entry()

if __name__ == "__main__":
    main()
