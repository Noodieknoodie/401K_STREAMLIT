# pages\client_dashboard\client_contact_management.py

import streamlit as st
from utils.utils import (
    get_contacts, add_contact, format_phone_number_ui, format_phone_number_db,
    validate_phone_number, delete_contact, update_contact, get_clients
)
from utils.ui_state_manager import UIStateManager
from utils.debug_logger import debug

def format_phone_on_change(phone_input: str) -> str:
    """Format phone number as user types"""
    if phone_input:
        return format_phone_number_ui(phone_input)
    return ''

def format_fax_on_change(fax_input: str) -> str:
    """Format fax number as user types"""
    if fax_input:
        return format_phone_number_ui(fax_input)
    return ''

@st.dialog('Contact Form')
def show_contact_form():
    """Display and handle the contact form dialog."""
    if 'ui_manager' not in st.session_state:
        return
    ui_manager = st.session_state.ui_manager
    
    if not ui_manager.is_contact_dialog_open:
        return
    
    state = ui_manager._get_dialog_state('contact')
    mode = state['mode']
    action = "Edit" if mode == "edit" else "Add"
    
    debug.log_ui_interaction(
        action=f"open_{mode}_contact_form",
        element="contact_dialog",
        data={"contact_type": state['contact_type']}
    )
    
    st.subheader(f"{action} {state['contact_type']} Contact")
    
    form_data = ui_manager.contact_form_data
    
    # Contact form fields
    name_key = f"contact_name_{state['contact_type']}"
    contact_name = st.text_input(
        "Name",
        key=name_key,
        value=form_data.get('contact_name', ''),
        on_change=lambda: ui_manager.clear_contact_validation_errors()
    )
    
    # Phone input with live formatting
    phone_key = f"phone_{state['contact_type']}"
    phone = st.text_input(
        "Phone",
        key=phone_key,
        value=form_data.get('phone', ''),
        on_change=lambda: ui_manager.update_contact_form_data({
            'phone': format_phone_on_change(st.session_state[phone_key])
        }),
        placeholder="5555555555"
    )
    
    # Fax input with live formatting
    fax_key = f"fax_{state['contact_type']}"
    fax = st.text_input(
        "Fax",
        key=fax_key,
        value=form_data.get('fax', ''),
        on_change=lambda: ui_manager.update_contact_form_data({
            'fax': format_fax_on_change(st.session_state[fax_key])
        }),
        placeholder="5555555555"
    )
    
    email_key = f"email_{state['contact_type']}"
    email = st.text_input(
        "Email",
        key=email_key,
        value=form_data.get('email', ''),
        on_change=lambda: ui_manager.clear_contact_validation_errors()
    )
    
    address_key = f"physical_address_{state['contact_type']}"
    physical_address = st.text_area(
        "Physical Address",
        key=address_key,
        value=form_data.get('physical_address', ''),
        on_change=lambda: ui_manager.clear_contact_validation_errors()
    )
    
    mailing_key = f"mailing_address_{state['contact_type']}"
    mailing_address = st.text_area(
        "Mailing Address",
        key=mailing_key,
        value=form_data.get('mailing_address', ''),
        on_change=lambda: ui_manager.clear_contact_validation_errors()
    )
    
    # Format phone numbers for database storage
    phone_db = format_phone_number_db(phone)
    fax_db = format_phone_number_db(fax)
    
    # Validate phone numbers
    if phone and not validate_phone_number(phone):
        debug.log_ui_interaction(
            action="validation_error",
            element="contact_form",
            data={"field": "phone", "error": "invalid_format"}
        )
        st.error("Please enter a valid 10-digit phone number")
        return
    
    if fax and not validate_phone_number(fax):
        debug.log_ui_interaction(
            action="validation_error",
            element="contact_form",
            data={"field": "fax", "error": "invalid_format"}
        )
        st.error("Please enter a valid 10-digit fax number")
        return
    
    # Update form data
    updated_data = {
        'contact_name': contact_name,
        'phone': phone_db,
        'fax': fax_db,
        'email': email,
        'physical_address': physical_address,
        'mailing_address': mailing_address
    }
    ui_manager.update_contact_form_data(updated_data)
    
    # Show validation errors
    if ui_manager.contact_dialog_has_errors:
        for error in ui_manager.contact_validation_errors:
            debug.log_ui_interaction(
                action="validation_error",
                element="contact_form",
                data={"error": error}
            )
            st.error(error)
    
    # Show cancel confirmation if needed
    if state['show_cancel_confirm']:
        debug.log_ui_interaction(
            action="show_cancel_confirm",
            element="contact_form",
            data={"mode": mode}
        )
        st.warning("You have unsaved changes. Are you sure you want to cancel?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes, Discard Changes", type="primary", use_container_width=True):
                debug.log_ui_interaction(
                    action="confirm_cancel",
                    element="contact_form",
                    data={"mode": mode}
                )
                ui_manager.close_contact_dialog()
                st.rerun()
        with col2:
            if st.button("No, Go Back", use_container_width=True):
                debug.log_ui_interaction(
                    action="cancel_discard",
                    element="contact_form",
                    data={"mode": mode}
                )
                state['show_cancel_confirm'] = False
                st.rerun()
    else:
        # Normal save/cancel buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Save", use_container_width=True):
                if any(value.strip() for value in updated_data.values()):
                    # Get client_id from session state
                    client_id = next(
                        client[0] for client in get_clients()
                        if client[1] == st.session_state.client_selector_dashboard
                    )
                    
                    debug.log_ui_interaction(
                        action=f"attempt_{mode}_contact",
                        element="contact_form",
                        data={
                            "client_id": client_id,
                            "contact_type": state['contact_type']
                        }
                    )
                    
                    if mode == "edit":
                        if update_contact(state['contact_id'], updated_data):
                            debug.log_ui_interaction(
                                action="contact_updated",
                                element="contact_form",
                                data={
                                    "contact_id": state['contact_id'],
                                    "contact_type": state['contact_type']
                                }
                            )
                            ui_manager.close_contact_dialog()
                            get_contacts.clear()
                            st.rerun()
                    else:
                        new_contact_id = add_contact(
                            client_id,
                            state['contact_type'],
                            updated_data
                        )
                        if new_contact_id:
                            debug.log_ui_interaction(
                                action="contact_added",
                                element="contact_form",
                                data={
                                    "contact_id": new_contact_id,
                                    "contact_type": state['contact_type']
                                }
                            )
                            ui_manager.close_contact_dialog()
                            get_contacts.clear()
                            st.rerun()
                else:
                    debug.log_ui_interaction(
                        action="validation_error",
                        element="contact_form",
                        data={"error": "empty_form"}
                    )
                    ui_manager.set_contact_validation_errors(["Please fill in at least one field."])
                    st.rerun()
        
        with col2:
            if st.button("Cancel", use_container_width=True):
                if any(value.strip() for value in updated_data.values()):
                    debug.log_ui_interaction(
                        action="show_cancel_confirm",
                        element="contact_form",
                        data={"mode": mode}
                    )
                    state['show_cancel_confirm'] = True
                    st.rerun()
                else:
                    debug.log_ui_interaction(
                        action="cancel_empty_form",
                        element="contact_form",
                        data={"mode": mode}
                    )
                    ui_manager.close_contact_dialog()
                    st.rerun()

def render_contact_card(contact, ui_manager: UIStateManager):
    """Render a single contact card with strict grid layout"""
    # Initialize delete confirmation state if needed
    if 'delete_contact_id' not in st.session_state:
        st.session_state.delete_contact_id = None
    if 'show_delete_confirm' not in st.session_state:
        st.session_state.show_delete_confirm = False
    
    # Main container for each contact
    with st.container():
        # Show delete confirmation if this is the contact being deleted
        if st.session_state.show_delete_confirm and st.session_state.delete_contact_id == contact[7]:
            debug.log_ui_interaction(
                action="show_delete_confirm",
                element="contact_card",
                data={
                    "contact_id": contact[7],
                    "contact_type": contact[0]
                }
            )
            confirm_col1, confirm_col2, confirm_col3 = st.columns([2,1,1])
            with confirm_col1:
                st.warning("Delete this contact?")
            with confirm_col2:
                if st.button("Yes", key=f"confirm_delete_{contact[7]}", type="primary"):
                    debug.log_ui_interaction(
                        action="confirm_delete",
                        element="contact_card",
                        data={
                            "contact_id": contact[7],
                            "contact_type": contact[0]
                        }
                    )
                    if delete_contact(contact[7]):
                        st.session_state.delete_contact_id = None
                        st.session_state.show_delete_confirm = False
                        get_contacts.clear()
                        st.rerun()
            with confirm_col3:
                if st.button("No", key=f"cancel_delete_{contact[7]}"):
                    debug.log_ui_interaction(
                        action="cancel_delete",
                        element="contact_card",
                        data={
                            "contact_id": contact[7],
                            "contact_type": contact[0]
                        }
                    )
                    st.session_state.delete_contact_id = None
                    st.session_state.show_delete_confirm = False
                    st.rerun()
            return

        # Two-column layout: Info | Actions
        info_col, action_col = st.columns([6, 1])
        
        with info_col:
            if contact[1]:  # Name
                st.text(contact[1])
            if contact[2]:  # Phone
                st.text(f"📞 {contact[2]}")
            if contact[3]:  # Email
                st.text(f"✉️ {contact[3]}")
            if contact[4]:  # Fax
                st.text(f"📠 {contact[4]}")
            if contact[5] or contact[6]:  # Addresses
                st.text(f"📍 {contact[5] or contact[6]}")
        
        with action_col:
            # Action buttons stacked vertically, right-aligned
            if st.button("✏️", key=f"edit_{contact[7]}", help="Edit contact"):
                debug.log_ui_interaction(
                    action="click_edit",
                    element="contact_card",
                    data={
                        "contact_id": contact[7],
                        "contact_type": contact[0]
                    }
                )
                ui_manager.open_contact_dialog(
                    contact_type=contact[0],
                    mode='edit',
                    contact_id=contact[7],
                    initial_data={
                        'contact_name': contact[1],
                        'phone': contact[2],
                        'email': contact[3],
                        'fax': contact[4],
                        'physical_address': contact[5],
                        'mailing_address': contact[6]
                    }
                )
                st.rerun()
            
            if st.button("🗑️", key=f"delete_{contact[7]}", help="Delete contact"):
                debug.log_ui_interaction(
                    action="click_delete",
                    element="contact_card",
                    data={
                        "contact_id": contact[7],
                        "contact_type": contact[0]
                    }
                )
                st.session_state.delete_contact_id = contact[7]
                st.session_state.show_delete_confirm = True
                st.rerun()
        
        # Minimal separator
        st.divider()