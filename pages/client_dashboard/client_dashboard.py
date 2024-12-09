import streamlit as st
from client_dashboard.client_contact_management import init_contact_form_state, show_contact_form
from client_dashboard.client_payment_management import show_payment_history
from client_dashboard.client_dashboard_metrics import show_client_metrics
from client_dashboard.client_selection import get_selected_client
from client_dashboard.client_contact_layout import show_contact_sections
from client_dashboard.client_payment_form import show_payment_form

def show_client_dashboard():
    """Main dashboard view with modular components."""
    st.write("👥 Client Dashboard")
    
    # Initialize contact form state
    init_contact_form_state()
    
    # Get selected client first
    client_id, selected_client_name = get_selected_client()
    
    # Show contact form dialog if open
    if 'contact_form' in st.session_state and st.session_state.contact_form['is_open']:
        show_contact_form()
    
    # Show payment form dialog if open
    if 'payment_form' in st.session_state and st.session_state.payment_form['is_open']:
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