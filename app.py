# app.py
import streamlit as st

# Configure the page - MUST be first Streamlit command
st.set_page_config(
    page_title="401K Payment Tracker",
    page_icon="💰",
    layout="wide",
)

# Initialize client selector if not present
if 'client_selector_dashboard' not in st.session_state:
    st.session_state.client_selector_dashboard = None

# Simple tab-based navigation
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Quarterly Summary",
    "👥 Client Dashboard", 
    "⚙️ Manage Clients",
    "📝 Bulk Payment Entry"
])

with tab1:
    from pages.main_summary.summary import show_main_summary
    show_main_summary()

with tab2:
    from pages.client_dashboard import show_client_dashboard
    show_client_dashboard()

with tab3:
    from pages.manage_clients.client_management import show_manage_clients
    show_manage_clients()

with tab4:
    from pages.bulk_payment.bulk_entry import show_bulk_payment_entry
    show_bulk_payment_entry()

