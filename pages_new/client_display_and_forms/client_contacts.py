"""
Contact Management Module Documentation
====================================

This module handles the contact management interface for the 401K Payment Tracker application.
It provides functionality for adding, editing, and viewing contacts with specific validation
and display requirements.

Key Components & Behaviors to Verify:
-----------------------------------

1. Contact Form Requirements:
   - Contact type selection (Primary/Authorized/Provider)
   - Required fields: Name for Primary contacts
   - Phone/Fax format: (555) 555-5555
   - Email validation
   - Physical/Mailing address fields
   - Real-time phone/fax formatting
   - Form validation before submission

2. Contact Display:
   - Three equal columns for contact types
   - Contact cards with icons:
     * 📞 Phone
     * ✉️ Email
     * 📠 Fax
     * 📍 Address
   - Actions: ✏️ (edit) and 🗑️ (delete)
   - Expandable sections per type
   - Contact count in headers

3. State Management:
   - Form state must reset after submission/cancellation
   - Delete confirmation must be exclusive
   - Edit state must be exclusive
   - Form validation state

4. Data Validation Rules:
   - Phone/Fax must be 10 digits
   - Email must be valid format
   - Primary contact name required
   - At least one field must be filled

Database Schema Dependencies:
---------------------------
- clients: client_id (primary key)
- contacts: contact_id, client_id (foreign key), contact_type, fields...

Required Utility Functions:
-------------------------
From utils.py:
- format_phone_number_ui: Formats phone/fax for display
- format_phone_number_db: Formats phone/fax for database
- validate_phone_number: Validates phone/fax format
- get_contacts: Retrieves contacts for a client
- add_contact: Adds new contact
- update_contact: Updates existing contact
- delete_contact: Deletes contact

Testing Checklist:
----------------
1. Form Validation:
   - Try submitting without required fields
   - Try invalid phone/fax formats
   - Try invalid email formats
   - Try empty form submission

2. Display Formatting:
   - Verify phone/fax formatting
   - Verify email display
   - Verify address display
   - Verify icon alignment
   - Verify card layout

3. State Management:
   - Verify form reset after actions
   - Verify delete confirmation flow
   - Verify edit form population
   - Verify validation state

4. Data Integrity:
   - Verify contact updates in database
   - Verify contact deletion
   - Verify type constraints
"""

import streamlit as st
from typing import Dict, Any, Optional, List
from utils.utils import (
    get_contacts,
    add_contact,
    update_contact,
    delete_contact,
    format_phone_number_ui,
    format_phone_number_db,
    validate_phone_number
)

# ============================================================================
# Contact Form State Management
# ============================================================================

def init_contact_state():
    """Initialize contact-related session state variables."""
    if 'show_contact_form' not in st.session_state:
        st.session_state.show_contact_form = False
    if 'contact_form_data' not in st.session_state:
        st.session_state.contact_form_data = {}
    if 'contact_edit_id' not in st.session_state:
        st.session_state.contact_edit_id = None
    if 'show_delete_confirm' not in st.session_state:
        st.session_state.show_delete_confirm = False
    if 'contact_validation_errors' not in st.session_state:
        st.session_state.contact_validation_errors = []
    if 'delete_contact_id' not in st.session_state:
        st.session_state.delete_contact_id = None

def reset_contact_form():
    """Reset contact form state."""
    st.session_state.show_contact_form = False
    st.session_state.contact_form_data = {}
    st.session_state.contact_edit_id = None
    st.session_state.contact_validation_errors = []

# ============================================================================
# Contact Form Display
# ============================================================================

def format_phone_on_change(field_key: str) -> None:
    """Format phone/fax number on input change."""
    if field_key in st.session_state:
        value = st.session_state[field_key]
        if value:
            formatted = format_phone_number_ui(value)
            st.session_state[field_key] = formatted

def show_contact_form(contact_type: str):
    """Display the contact form for adding/editing contacts."""
    with st.form("contact_form", clear_on_submit=False):
        st.subheader(f"{'Edit' if st.session_state.contact_edit_id else 'Add'} {contact_type} Contact")
        
        # Contact fields
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input(
                "Name" + (" *" if contact_type == "Primary" else ""),
                value=st.session_state.contact_form_data.get('contact_name', ''),
                key="contact_name"
            )
            
            phone = st.text_input(
                "Phone",
                value=st.session_state.contact_form_data.get('phone', ''),
                key="phone",
                placeholder="5555555555"
            )
            st.caption("Enter 10 digits without formatting")
            
            email = st.text_input(
                "Email",
                value=st.session_state.contact_form_data.get('email', ''),
                key="email"
            )
        
        with col2:
            fax = st.text_input(
                "Fax",
                value=st.session_state.contact_form_data.get('fax', ''),
                key="fax",
                placeholder="5555555555"
            )
            st.caption("Enter 10 digits without formatting")
            
            physical_address = st.text_area(
                "Physical Address",
                value=st.session_state.contact_form_data.get('physical_address', ''),
                key="physical_address",
                height=100
            )
            
            mailing_address = st.text_area(
                "Mailing Address",
                value=st.session_state.contact_form_data.get('mailing_address', ''),
                key="mailing_address",
                height=100
            )
        
        # Show validation errors if any
        if st.session_state.contact_validation_errors:
            for error in st.session_state.contact_validation_errors:
                st.error(error)
        
        # Submit/Cancel buttons
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("Save", type="primary", use_container_width=True)
        with col2:
            cancelled = st.form_submit_button("Cancel", use_container_width=True)
        
        if submitted:
            # Prepare form data
            form_data = {
                'contact_name': name,
                'phone': format_phone_number_db(phone) if phone else '',
                'email': email,
                'fax': format_phone_number_db(fax) if fax else '',
                'physical_address': physical_address,
                'mailing_address': mailing_address
            }
            
            # Validate form data
            validation_errors = validate_contact_data(form_data, contact_type)
            if validation_errors:
                st.session_state.contact_validation_errors = validation_errors
                st.rerun()
            else:
                if st.session_state.contact_edit_id:
                    if update_contact(st.session_state.contact_edit_id, form_data):
                        st.success("Contact updated successfully!")
                        reset_contact_form()
                        st.rerun()
                    else:
                        st.error("Failed to update contact")
                else:
                    if add_contact(st.session_state.client_id, contact_type, form_data):
                        st.success("Contact added successfully!")
                        reset_contact_form()
                        st.rerun()
                    else:
                        st.error("Failed to add contact")
        
        elif cancelled:
            reset_contact_form()
            st.rerun()

def validate_contact_data(data: Dict[str, Any], contact_type: str) -> List[str]:
    """Validate contact form data."""
    errors = []
    
    # Check required name for Primary contacts
    if contact_type == "Primary" and not data['contact_name'].strip():
        errors.append("Name is required for Primary contacts")
    
    # Validate phone number if provided
    if data['phone'] and not validate_phone_number(data['phone']):
        errors.append("Please enter a valid 10-digit phone number")
    
    # Validate fax number if provided
    if data['fax'] and not validate_phone_number(data['fax']):
        errors.append("Please enter a valid 10-digit fax number")
    
    # Validate email if provided
    if data['email'] and '@' not in data['email']:
        errors.append("Please enter a valid email address")
    
    # Ensure at least one field is filled
    if not any(value.strip() for value in data.values()):
        errors.append("Please fill in at least one field")
    
    return errors

# ============================================================================
# Contact Display
# ============================================================================

def show_contact_sections(client_id: int):
    """Display the contact sections in a three-column layout."""
    # Get contacts data
    contacts = get_contacts(client_id)
    
    # Group contacts by type
    contact_types = {'Primary': [], 'Authorized': [], 'Provider': []}
    if contacts:
        for contact in contacts:
            if contact[0] in contact_types:
                contact_types[contact[0]].append(contact)
    
    # Create three equal-width columns
    c1, c2, c3 = st.columns(3)
    
    # Primary Contacts
    with c1:
        render_contact_section('Primary', contact_types['Primary'])
    
    # Authorized Contacts
    with c2:
        render_contact_section('Authorized', contact_types['Authorized'])
    
    # Provider Contacts
    with c3:
        render_contact_section('Provider', contact_types['Provider'])

def render_contact_section(contact_type: str, contacts: list):
    """Render a contact section with its contacts and add button."""
    with st.expander(f"{contact_type} Contact ({len(contacts)})", expanded=False):
        if contacts:
            for contact in contacts:
                render_contact_card(contact, contact_type)
        else:
            st.caption(f"No {contact_type.lower()} contacts")
        
        if st.button(f"Add {contact_type} Contact", key=f"add_{contact_type.lower()}", use_container_width=True):
            st.session_state.show_contact_form = True
            st.session_state.contact_type = contact_type
            st.rerun()

def render_contact_card(contact, contact_type: str):
    """Render a single contact card.
    
    Args:
        contact: The contact data tuple
        contact_type: The type of contact (Primary/Authorized/Provider)
    """
    with st.container():
        # Show delete confirmation if this is the contact being deleted
        if st.session_state.show_delete_confirm and st.session_state.delete_contact_id == contact[7]:
            st.warning("Delete this contact?")
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("Yes", key=f"confirm_delete_contact_{contact_type}_{contact[7]}", type="primary"):
                    if delete_contact(contact[7]):
                        st.session_state.delete_contact_id = None
                        st.session_state.show_delete_confirm = False
                        st.rerun()
            with col2:
                if st.button("No", key=f"cancel_delete_contact_{contact_type}_{contact[7]}"):
                    st.session_state.delete_contact_id = None
                    st.session_state.show_delete_confirm = False
                    st.rerun()
            return
            
        # Contact info
        st.write(f"**{contact[1]}**")  # Name
        if contact[2]:  # Phone
            st.write(f"📞 {contact[2]}")
        if contact[3]:  # Email
            st.write(f"✉️ {contact[3]}")
        if contact[4]:  # Fax
            st.write(f"📠 {contact[4]}")
        if contact[5] or contact[6]:  # Addresses
            st.write(f"📍 {contact[5] or contact[6]}")
            
        # Actions
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("✏️", key=f"edit_contact_{contact_type}_{contact[7]}", help="Edit contact"):
                st.session_state.contact_edit_id = contact[7]
                st.session_state.contact_type = contact[0]
                st.session_state.contact_form_data = {
                    'contact_name': contact[1],
                    'phone': contact[2],
                    'email': contact[3],
                    'fax': contact[4],
                    'physical_address': contact[5],
                    'mailing_address': contact[6]
                }
                st.session_state.show_contact_form = True
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"delete_contact_{contact_type}_{contact[7]}", help="Delete contact"):
                st.session_state.delete_contact_id = contact[7]
                st.session_state.show_delete_confirm = True
                st.rerun()
                
        st.divider()

# ============================================================================
# Main Display Function
# ============================================================================

def display_contacts_section(client_id: int):
    """Main entry point for the contacts section."""
    # Initialize state
    init_contact_state()
    st.session_state.client_id = client_id
    
    # Show form or sections
    if st.session_state.show_contact_form:
        show_contact_form(st.session_state.contact_type)
    else:
        show_contact_sections(client_id)

if __name__ == "__main__":
    st.set_page_config(page_title="Client Contacts", layout="wide")
    # For testing
    display_contacts_section(1)
