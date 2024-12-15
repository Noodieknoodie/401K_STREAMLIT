# pages\client_dashboard\client_dashboard.py

import streamlit as st
from .client_contact_management import (
    show_contact_form,
)
from .client_payment_management import (
    show_payment_history
)
from .client_dashboard_metrics import show_client_metrics
from .client_selection import get_selected_client
from .client_contact_layout import show_contact_sections
from .client_payment_form import show_payment_dialog
from utils.client_data import (  
    get_client_details_optimized as get_client_details,
    get_contacts_optimized as get_contacts
)
from utils.perf_logging import log_ui_action, log_event
from utils.ui_state_manager import UIStateManager
from utils.debug_logger import debug
import time

def display_client_dashboard():
    """Main dashboard display function"""
    start_time = time.time()
    
    debug.log_ui_interaction(
        action='display_dashboard',
        element='client_dashboard',
        data={'timestamp': start_time}
    )
    
    # Initialize UI state manager
    ui_manager = UIStateManager()
    debug.log_state_change(
        component='ui_manager',
        old_value=None,
        new_value='initialized',
        context={'action': 'initialize_dashboard'}
    )
    
    # Get selected client (this needs to run always)
    selected_client = get_selected_client()
    debug.log_ui_interaction(
        action='client_selection',
        element='client_selector',
        data={'selected_client': selected_client[1] if selected_client else None}
    )
    
    if selected_client:
        client_id = selected_client[0]
        
        # Log performance metrics
        log_event("dashboard_load_start", {"client_id": client_id})
        debug.log_ui_interaction(
            action='dashboard_load',
            element='client_dashboard',
            data={'client_id': client_id, 'status': 'start'}
        )
        
        # Show dashboard components
        show_client_metrics(client_id)
        show_contact_sections(client_id, ui_manager)
        show_payment_history(client_id, ui_manager)
        
        # Show dialogs if needed - only show one at a time
        # The UIStateManager ensures mutual exclusivity
        if ui_manager.is_payment_dialog_open:
            debug.log_ui_interaction(
                action='show_dialog',
                element='payment_dialog',
                data={'client_id': client_id, 'dialog_type': 'payment'}
            )
            show_payment_dialog(client_id)
        elif ui_manager.is_contact_dialog_open:
            debug.log_ui_interaction(
                action='show_dialog',
                element='contact_dialog',
                data={'client_id': client_id, 'dialog_type': 'contact'}
            )
            show_contact_form()
        
        # Log performance metrics
        end_time = time.time()
        load_time = end_time - start_time
        
        log_event("dashboard_load_complete", {
            "client_id": client_id,
            "load_time": load_time
        })
        
        debug.log_ui_interaction(
            action='dashboard_load',
            element='client_dashboard',
            data={
                'client_id': client_id,
                'status': 'complete',
                'load_time': load_time
            }
        )
    else:
        debug.log_ui_interaction(
            action='dashboard_load',
            element='client_dashboard',
            data={'status': 'no_client_selected'}
        )
        st.info("Please select a client to view their dashboard.")

# Keep the old function name for backward compatibility
@log_ui_action("show_dashboard")
def show_client_dashboard():
    """Wrapper for display_client_dashboard to maintain backward compatibility"""
    debug.log_ui_interaction(
        action='show_dashboard',
        element='client_dashboard',
        data={'wrapper_called': True}
    )
    st.write("👥 Client Dashboard")
    display_client_dashboard()