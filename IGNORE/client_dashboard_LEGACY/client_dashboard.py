# # pages\client_dashboard\client_dashboard.py
# 
# import streamlit as st
# from .client_contact_management import (
#     show_contact_form,
# )
# from .client_payment_management import (
#     show_payment_history
# )
# from .client_dashboard_metrics import show_client_metrics
# from .client_selection import get_selected_client
# from .client_contact_layout import show_contact_sections
# from .client_payment_form import show_payment_dialog
# from .client_contract_management import show_contract_management_dialog
# from utils.client_data import (  
#     get_client_details_optimized as get_client_details,
#     get_contacts_optimized as get_contacts
# )
# from utils.ui_state_manager import UIStateManager
# import time
# 
# def display_client_dashboard():
#     """Main dashboard display function"""
#     start_time = time.time()
# 
#     # Initialize UI state manager
#     ui_manager = UIStateManager()
# 
#     # Get selected client (this needs to run always)
#     selected_client = get_selected_client()
#     if selected_client:
#         client_id = selected_client[0]
# 
#         # Show dashboard components
#         show_client_metrics(client_id)
#         show_contact_sections(client_id, ui_manager)
#         show_payment_history(client_id, ui_manager)
# 
#         # Show dialogs if needed - only show one at a time
#         # The UIStateManager ensures mutual exclusivity
#         if ui_manager.is_payment_dialog_open:
#             show_payment_dialog(client_id)
#         elif ui_manager.is_contact_dialog_open:
#             show_contact_form()
#         elif ui_manager.is_contract_dialog_open:
#             show_contract_management_dialog(client_id)
# 
#         # Log performance metrics (Removed)
#         end_time = time.time()
#         load_time = end_time - start_time
#         # Removed log_event call
#     else:
#         st.info("Please select a client to view their dashboard.")
# 
# # Keep the old function name for backward compatibility
# def show_client_dashboard():
#     """Wrapper for display_client_dashboard to maintain backward compatibility"""
#     st.write("👥 Client Dashboard")
#     display_client_dashboard()
