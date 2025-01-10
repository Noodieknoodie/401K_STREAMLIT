# app.py
import streamlit as st

# Configure the page - MUST be first Streamlit command
st.set_page_config(
    page_title="401K Payment Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Simple tab-based navigation
tabs = st.tabs([
    "📊 Quarterly Summary",
    "👥 Client Dashboard", 
    "⚙️ Manage Clients",
    "📝 Bulk Payment Entry",
    "📊 Export Data"
])

# Render the selected page based on tab
with tabs[0]:  # Quarterly Summary
    from pages_new.main_summary.summary import show_main_summary
    show_main_summary()

with tabs[1]:  # Client Dashboard
    from pages_new.client_display_and_forms.client_dashboard import show_client_dashboard
    show_client_dashboard()

with tabs[2]:  # Manage Clients
    from pages_new.manage_clients.client_management import show_manage_clients
    show_manage_clients()

with tabs[3]:  # Bulk Payment Entry
    from pages_new.bulk_payment.bulk_entry import show_bulk_payment_entry
    show_bulk_payment_entry()

with tabs[4]:  # Export Data
    try:
        from pages_new.document_export import show_export_data
        show_export_data()
    except Exception as e:
        st.error(f"Error loading export module: {str(e)}")
        st.error("Please check the console for more details.")
    