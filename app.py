import streamlit as st
from sidebar import render_sidebar
from styles import load_styles
from quarterly_summary import show_quarterly_summary
from client_dashboard import show_client_dashboard
from manage_clients import show_manage_clients
from bulk_payment_entry import show_bulk_payment_entry

# Set page config
st.set_page_config(
    page_title="401K Payment Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load and apply all styles
st.markdown(load_styles(), unsafe_allow_html=True)

def main():
    # Initialize session state for navigation
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'Quarterly Summary'
    if 'selected_client' not in st.session_state:
        st.session_state.selected_client = None

    # Render sidebar
    render_sidebar()

    # Main content area
    if st.session_state.current_page == 'Quarterly Summary':
        show_quarterly_summary()
    elif st.session_state.current_page == 'Client Dashboard':
        show_client_dashboard()
    elif st.session_state.current_page == 'Manage Clients':
        show_manage_clients()
    elif st.session_state.current_page == 'Bulk Payment Entry':
        show_bulk_payment_entry()

if __name__ == "__main__":
    main()