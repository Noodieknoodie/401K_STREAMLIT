# pages\client_dashboard\client_contact_layout.py

import streamlit as st
from utils.utils import get_contacts
from .client_contact_management import render_contact_card, show_contact_form
from utils.debug_logger import debug

def render_contact_section(contact_type: str, contacts: list, ui_manager=None):
    """Render a contact section with its contacts and add button
    
    Args:
        contact_type: The type of contacts to display (Primary, Authorized, Provider)
        contacts: List of contacts of this type
        ui_manager: Optional UIStateManager instance for dialog coordination
    """
    debug.log_ui_interaction(
        action='render_section',
        element=f'{contact_type}_contact_section',
        data={'contact_count': len(contacts)}
    )
    
    with st.expander(f"{contact_type} Contact ({len(contacts)})", expanded=False):
        if contacts:
            for contact in contacts:
                render_contact_card(contact, ui_manager)
        else:
            st.caption(f"No {contact_type.lower()} contacts")
        
        if st.button(f"Add {contact_type} Contact", key=f"add_{contact_type.lower()}", use_container_width=True):
            debug.log_ui_interaction(
                action='button_click',
                element=f'add_{contact_type.lower()}_contact',
                data={'contact_type': contact_type}
            )
            
            if ui_manager:
                old_state = getattr(st.session_state, 'ui_manager', None)
                st.session_state.ui_manager = ui_manager  # Store for dialog access
                debug.log_state_change(
                    component='ui_manager',
                    old_value='previous_state',
                    new_value='updated_state',
                    context={
                        'action': 'store_ui_manager',
                        'contact_type': contact_type
                    }
                )
                
                ui_manager.open_contact_dialog(
                    contact_type=contact_type,
                    mode='add'
                )
                debug.log_ui_interaction(
                    action='open_dialog',
                    element='contact_dialog',
                    data={'contact_type': contact_type, 'mode': 'add'}
                )
                
                show_contact_form()
                st.rerun()

def show_contact_sections(client_id: int, ui_manager=None):
    """Display the contact sections in a three-column layout.
    
    Args:
        client_id: The ID of the client whose contacts to display
        ui_manager: Optional UIStateManager instance for dialog coordination
    """
    debug.log_ui_interaction(
        action='show_sections',
        element='contact_sections',
        data={'client_id': client_id}
    )
    
    # Get contacts data
    contacts = get_contacts(client_id)
    debug.log_db_operation(
        operation='fetch',
        table='contacts',
        data={'client_id': client_id},
        result={'contact_count': len(contacts) if contacts else 0}
    )
    
    contact_types = {'Primary': [], 'Authorized': [], 'Provider': []}
    if contacts:
        for contact in contacts:
            if contact[0] in contact_types:
                contact_types[contact[0]].append(contact)
    
    # Create three equal-width columns for contact cards
    c1, c2, c3 = st.columns(3)
    
    # Primary Contacts Card
    with c1:
        render_contact_section('Primary', contact_types['Primary'], ui_manager)
    
    # Authorized Contacts Card
    with c2:
        render_contact_section('Authorized', contact_types['Authorized'], ui_manager)
    
    # Provider Contacts Card
    with c3:
        render_contact_section('Provider', contact_types['Provider'], ui_manager)