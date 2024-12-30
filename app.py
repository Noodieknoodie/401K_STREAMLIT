import streamlit as st

# Configure the page - MUST be first Streamlit command
st.set_page_config(
    page_title="401K Payment Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize sidebar state if not exists
if 'sidebar_state' not in st.session_state:
    st.session_state.sidebar_state = 'collapsed'

# Updated CSS injection
st.markdown("""
<style>
/* Expanded sidebar container */
[data-testid="stSidebar"][aria-expanded="true"] {
    width: 40% !important;
    max-width: 40% !important;
}

/* Expanded sidebar content */
[data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
    width: 40% !important;
    max-width: 40% !important;
}

/* Main content when sidebar is expanded */
[data-testid="stSidebar"][aria-expanded="true"] ~ .main {
    margin-left: 40% !important;
    width: 60% !important;
    max-width: 60% !important;
}
</style>
""", unsafe_allow_html=True)

# Now we can import modules that use Streamlit
import sidebar  # Import sidebar after set_page_config

# Simple tab-based navigation
tabs = st.tabs([
    "📊 Quarterly Summary",
    "👥 Client Dashboard", 
    "⚙️ Manage Clients",
    "📝 Bulk Payment Entry"
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
