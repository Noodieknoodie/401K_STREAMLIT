import streamlit as st
from .client_contact_management import init_contact_form_state, show_contact_form
from .client_payment_management import show_payment_history, clear_client_specific_states, init_payment_form_state
from .client_dashboard_metrics import show_client_metrics
from .client_selection import get_selected_client
from .client_contact_layout import show_contact_sections
from .client_payment_form import show_payment_form

def show_client_dashboard():
    """Main dashboard view with modular components."""
    st.write("👥 Client Dashboard")
    
    # Get selected client first
    client_id, selected_client_name = get_selected_client()
    
    # Reset state when changing clients - MOVED BEFORE state initialization
    if 'previous_client' not in st.session_state:
        st.session_state.previous_client = None
    
    # Clear states if client changed - MOVED BEFORE state initialization
    if selected_client_name != "Select a client..." and st.session_state.previous_client != selected_client_name:
        clear_client_specific_states()
        st.session_state.previous_client = selected_client_name
    
    # Initialize all states AFTER clearing
    init_contact_form_state()
    init_payment_form_state()
    
    # Show contact form dialog if open
    if 'contact_form' in st.session_state and st.session_state.contact_form['is_open']:
        show_contact_form()
    
    # Show payment form dialog if open - Updated to verify client_id
    if ('payment_form' in st.session_state and 
        st.session_state.payment_form['is_visible'] and 
        (st.session_state.payment_form['client_id'] is None or  # New form
         st.session_state.payment_form['client_id'] == client_id)):  # Existing form for current client
        st.session_state.payment_form['client_id'] = client_id  # Set client_id for new forms
        show_payment_form(client_id)
    
    if client_id:
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