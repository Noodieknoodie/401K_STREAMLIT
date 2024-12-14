import streamlit as st
from utils.client_data import get_contacts_optimized as get_contacts
from .client_contact_management import render_contact_section, render_contact_card
from utils.debug_logger import debug

def render_contact_sections(client_id):
    """Display the contact sections in a three-column layout."""
    # Get contacts data
    contacts = get_contacts(client_id)
    contact_types = {'Primary': [], 'Authorized': [], 'Provider': []}
    
    debug.log_ui_interaction(
        action="load_contact_sections",
        element="contact_layout",
        data={
            "client_id": client_id,
            "total_contacts": len(contacts) if contacts else 0
        }
    )
    
    if contacts:
        for contact in contacts:
            try:
                contact_type = contact[0] if contact and len(contact) > 0 else None
                if contact_type in contact_types:
                    contact_types[contact_type].append(contact)
            except (IndexError, TypeError) as e:
                debug.log_ui_interaction(
                    action="contact_processing_error",
                    element="contact_layout",
                    data={
                        "error": str(e),
                        "contact_data": str(contact)
                    }
                )
                st.error(f"Error processing contact data: {str(e)}")
                continue  # Skip invalid contact data
    
    # Log contact type distribution
    debug.log_ui_interaction(
        action="contact_distribution",
        element="contact_layout",
        data={
            "primary_count": len(contact_types['Primary']),
            "authorized_count": len(contact_types['Authorized']),
            "provider_count": len(contact_types['Provider'])
        }
    )
    
    # Create three equal-width columns for contact cards
    c1, c2, c3 = st.columns(3)
    
    # Primary Contacts Card
    with c1:
        render_contact_section('Primary', contact_types['Primary'])
    
    # Authorized Contacts Card
    with c2:
        render_contact_section('Authorized', contact_types['Authorized'])
    
    # Provider Contacts Card
    with c3:
        render_contact_section('Provider', contact_types['Provider']) 