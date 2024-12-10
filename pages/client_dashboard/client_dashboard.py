import streamlit as st
from .client_contact_management import init_contact_form_state, show_contact_form
from .client_payment_management import show_payment_history, clear_client_specific_states, init_payment_form_state
from .client_dashboard_metrics import show_client_metrics
from .client_selection import get_selected_client
from .client_contact_layout import show_contact_sections
from .client_payment_form import show_payment_form
from utils.client_data import (  # New optimized queries
    get_consolidated_client_data,
    get_client_details_optimized as get_client_details,
    get_contacts_optimized as get_contacts
)
from utils.perf_logging import log_ui_action, log_event
import time

@log_ui_action("show_dashboard")
def show_client_dashboard():
    """Main dashboard view with modular components."""
    st.write("👥 Client Dashboard")
    
    # Initialize base states first
    init_contact_form_state()
    init_payment_form_state()
    
    # Get selected client
    client_id, selected_client_name = get_selected_client()
    
    # Log client selection
    if selected_client_name != "Select a client...":
        log_event('client_selected', {'client': selected_client_name})
    
    # Initialize previous client tracking if needed
    if 'previous_client' not in st.session_state:
        st.session_state.previous_client = None
    
    # Clear client-specific states only when switching clients
    if selected_client_name != "Select a client..." and st.session_state.previous_client != selected_client_name:
        clear_client_specific_states()
        st.session_state.previous_client = selected_client_name
    
    # Show contact form dialog if open
    if 'contact_form' in st.session_state and st.session_state.contact_form['is_open']:
        log_event('contact_form_opened', {'type': st.session_state.contact_form.get('contact_type')})
        show_contact_form()
    
    # Show payment form dialog if open
    if ('payment_form' in st.session_state and 
        st.session_state.payment_form['is_visible']):
        log_event('payment_form_opened', {'client_id': client_id})
        show_payment_form(client_id)
    
    if client_id:
        start_time = time.time()
        # Get all client data in a single query
        client_data = get_consolidated_client_data(client_id)
        if client_data:
            # Log data load time
            log_event('client_data_loaded', {
                'client': selected_client_name,
                'has_contract': bool(client_data['active_contract']),
                'has_payments': bool(client_data['latest_payment']),
                'contact_count': len(client_data['contacts'])
            }, time.time() - start_time)
            
            # Show client metrics
            show_client_metrics(client_id)

            # Small spacing before contacts section
            st.markdown("<div style='margin: 0.5rem 0;'></div>", unsafe_allow_html=True)
            
            # Show contact sections
            show_contact_sections(client_id)
            
            # Payments History Section
            st.markdown("<div style='margin: 2rem 0 1rem 0;'></div>", unsafe_allow_html=True)
            st.markdown("### Payment History")
            
            show_payment_history(client_id) 