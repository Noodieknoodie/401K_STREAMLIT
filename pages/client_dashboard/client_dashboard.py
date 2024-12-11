import streamlit as st
from .client_contact_management import (
    init_contact_form_state,
    show_contact_form,
    open_contact_form
)
from .client_payment_management import (
    show_payment_history,
    clear_client_specific_states,
    init_notes_state,
    init_filter_state,
    format_payment_data
)
from .client_dashboard_metrics import show_client_metrics
from .client_selection import get_selected_client
from .client_contact_layout import show_contact_sections
from .client_payment_form import (
    init_payment_form,
    show_payment_form
)
from utils.client_data import (  
    get_consolidated_client_data,
    get_client_details_optimized as get_client_details,
    get_contacts_optimized as get_contacts
)
from utils.perf_logging import log_ui_action, log_event
from utils.ui_state_manager import UIStateManager
import time

def lazy_init_form_states():
    """Lazily initialize form states only when needed"""
    # Initialize all states at once if any form will be shown
    if (('payment_form' not in st.session_state or 
         st.session_state.get('payment_form', {}).get('is_visible', False)) or
        ('contact_form' not in st.session_state or 
         st.session_state.get('contact_form', {}).get('is_open', False))):
        init_payment_form()
        init_contact_form_state()
        init_notes_state()
        init_filter_state()

def display_client_dashboard():
    """Main dashboard display function"""
    start_time = time.time()
    
    # Initialize UI state manager
    ui_manager = UIStateManager()
    
    # Get selected client (this needs to run always)
    selected_client = get_selected_client()
    
    if selected_client:
        client_id = selected_client[0]
        
        # Lazy initialize forms only when we have a selected client
        lazy_init_form_states()
        
        # Log performance metrics
        log_event("dashboard_load_start", {"client_id": client_id})
        
        # Show dashboard components
        show_client_metrics(client_id)  # Pass client_id instead of tuple
        show_contact_sections(client_id, ui_manager)  # Pass ui_manager to contact sections
        show_payment_history(client_id, ui_manager)  # Pass ui_manager to coordinate note states
        
        # Show forms if needed - only show one at a time
        # The UIStateManager ensures mutual exclusivity
        if ui_manager.is_payment_form_visible:
            show_payment_form(client_id)
        elif ui_manager.is_contact_form_open:
            show_contact_form()
        
        # Log performance metrics
        end_time = time.time()
        log_event("dashboard_load_complete", {
            "client_id": client_id,
            "load_time": end_time - start_time
        })
    else:
        st.info("Please select a client to view their dashboard.")

# Keep the old function name for backward compatibility
@log_ui_action("show_dashboard")
def show_client_dashboard():
    """Wrapper for display_client_dashboard to maintain backward compatibility"""
    st.write("👥 Client Dashboard")
    display_client_dashboard()