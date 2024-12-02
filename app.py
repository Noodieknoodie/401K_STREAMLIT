import streamlit as st
from sidebar import render_sidebar
from pages.quarterly_summary import render_quarterly_summary
from pages.client_dashboard import render_client_dashboard
from pages.manage_clients import render_manage_clients
from pages.bulk_payment_entry import render_bulk_payment_entry

# Set page config
st.set_page_config(
    page_title="401K Payment Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for navigation
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Quarterly Summary'
if 'selected_client' not in st.session_state:
    st.session_state.selected_client = None

# Render sidebar
render_sidebar()

# Render the appropriate page based on navigation state
if st.session_state.current_page == 'Quarterly Summary':
    render_quarterly_summary()
elif st.session_state.current_page == 'Client Dashboard':
    render_client_dashboard()
elif st.session_state.current_page == 'Manage Clients':
    render_manage_clients()
elif st.session_state.current_page == 'Bulk Payment Entry':
    render_bulk_payment_entry() 