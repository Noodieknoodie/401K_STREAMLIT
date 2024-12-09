import streamlit as st
from .contact_management import show_contact_form
from .payment_management import show_payment_history
from .dashboard_metrics import show_client_metrics
from .client_selection import get_selected_client
from .contact_layout import show_contact_sections
from .payment_form import show_payment_form
from .state_management import DashboardState, PaymentFormState, ContactFormState

def show_client_dashboard():
    """Main dashboard view with modular components."""
    st.write("👥 Client Dashboard")
    
    # Initialize all dashboard states
    DashboardState.initialize()
    
    # Get selected client first
    client_id, selected_client_name = get_selected_client()
    
    # Show contact form dialog if open
    if ContactFormState.is_open():
        show_contact_form()
    
    # Show payment form dialog if open
    if PaymentFormState.is_open():
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