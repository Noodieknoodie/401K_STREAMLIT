import streamlit as st
from utils.utils import get_contacts
from .client_contact_management import render_contact_section

def show_contact_sections(client_id, ui_manager=None):
    """Display the contact sections in a three-column layout."""
    # Get contacts data
    contacts = get_contacts(client_id)
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