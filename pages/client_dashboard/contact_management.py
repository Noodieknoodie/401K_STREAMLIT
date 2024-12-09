import streamlit as st
from utils.utils import (
    get_contacts, add_contact, format_phone_number_ui, format_phone_number_db,
    validate_phone_number, delete_contact, update_contact, get_clients
)
from .state_management import ContactFormState

def format_phone_on_change():
    """Format phone number as user types"""
    ContactFormState.set_validation_error(False)
    key = f"phone_{st.session_state.contact_form['contact_type']}"
    if key in st.session_state:
        st.session_state.contact_form['form_data']['phone'] = format_phone_number_ui(st.session_state[key])

def format_fax_on_change():
    """Format fax number as user types"""
    ContactFormState.set_validation_error(False)
    key = f"fax_{st.session_state.contact_form['contact_type']}"
    if key in st.session_state:
        st.session_state.contact_form['form_data']['fax'] = format_phone_number_ui(st.session_state[key])

@st.dialog('Contact Form')
def show_contact_form():
    """Display the contact form dialog"""
    ContactFormState.initialize()
    
    if not ContactFormState.is_open():
        return
    
    mode = st.session_state.contact_form.get('mode', 'add')
    action = "Edit" if mode == "edit" else "Add"
    contact_type = st.session_state.contact_form.get('contact_type')
    
    st.subheader(f"{action} {contact_type} Contact")
    
    # Show validation error if present
    if ContactFormState.has_validation_error():
        st.error("Please fill in at least one field.")
    
    # Contact form fields
    contact_name = st.text_input(
        "Name",
        key=f"contact_name_{contact_type}",
        value=st.session_state.contact_form['form_data']['contact_name'],
        on_change=lambda: ContactFormState.set_validation_error(False)
    )
    
    # Phone input with live formatting
    phone_input = st.text_input(
        "Phone",
        key=f"phone_{contact_type}",
        value=st.session_state.contact_form['form_data']['phone'],
        on_change=format_phone_on_change,
        placeholder="5555555555"
    )
    
    # Fax input with live formatting
    fax_input = st.text_input(
        "Fax",
        key=f"fax_{contact_type}",
        value=st.session_state.contact_form['form_data']['fax'],
        on_change=format_fax_on_change,
        placeholder="5555555555"
    )
    
    email = st.text_input(
        "Email",
        key=f"email_{contact_type}",
        value=st.session_state.contact_form['form_data']['email'],
        on_change=lambda: ContactFormState.set_validation_error(False)
    )
    
    physical_address = st.text_area(
        "Physical Address",
        key=f"physical_address_{contact_type}",
        value=st.session_state.contact_form['form_data']['physical_address'],
        on_change=lambda: ContactFormState.set_validation_error(False)
    )
    
    mailing_address = st.text_area(
        "Mailing Address",
        key=f"mailing_address_{contact_type}",
        value=st.session_state.contact_form['form_data']['mailing_address'],
        on_change=lambda: ContactFormState.set_validation_error(False)
    )
    
    # Format phone numbers for database storage
    phone_db = format_phone_number_db(phone_input)
    fax_db = format_phone_number_db(fax_input)
    
    # Capture form data
    form_data = {
        'contact_name': contact_name,
        'phone': phone_db,
        'fax': fax_db,
        'email': email,
        'physical_address': physical_address,
        'mailing_address': mailing_address
    }
    
    # Show cancel confirmation if needed
    if st.session_state.contact_form['show_cancel_confirm']:
        st.warning("You have unsaved changes. Are you sure you want to cancel?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes, Discard Changes", type="primary", use_container_width=True):
                print("\n❌ Form cancelled - changes discarded")
                ContactFormState.clear()
                st.rerun()
        with col2:
            if st.button("No, Go Back", use_container_width=True):
                st.session_state.contact_form['show_cancel_confirm'] = False
                st.rerun()
    else:
        # Normal save/cancel buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Save", use_container_width=True):
                if any(value.strip() for value in form_data.values()):
                    try:
                        # Get client_id from session state
                        client_id = next(
                            client[0] for client in get_clients()
                            if client[1] == st.session_state.client_selector_dashboard
                        )
                        
                        if mode == "edit":
                            # Update existing contact
                            if update_contact(st.session_state.contact_form['contact_id'], form_data):
                                print(f"\n✅ Successfully updated {contact_type} contact in database:")
                                for field, value in form_data.items():
                                    print(f"  {field}: {value}")
                                ContactFormState.clear()
                                get_contacts.clear()  # Clear the contacts cache
                                st.rerun()
                            else:
                                st.error("Failed to update contact. Please try again.")
                        else:
                            # Add new contact
                            contact_id = add_contact(
                                client_id,
                                contact_type,
                                form_data
                            )
                            
                            if contact_id:
                                print(f"\n✅ Successfully added {contact_type} contact to database:")
                                for field, value in form_data.items():
                                    print(f"  {field}: {value}")
                                ContactFormState.clear()
                                get_contacts.clear()  # Clear the contacts cache
                                st.rerun()
                            else:
                                st.error("Failed to add contact. Please try again.")
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
                        print(f"\n❌ Error saving contact: {str(e)}")
                else:
                    ContactFormState.set_validation_error(True)
                st.rerun()
        
        with col2:
            if st.button("Cancel", use_container_width=True):
                if any(value.strip() for value in st.session_state.contact_form['form_data'].values()):
                    st.session_state.contact_form['show_cancel_confirm'] = True
                    st.rerun()
                else:
                    print("\n❌ Form cancelled - no changes to discard")
                    ContactFormState.clear()
                    st.rerun()

def render_contact_card(contact):
    """Render a single contact card with strict grid layout"""
    # Main container for each contact
    with st.container():
        # Show delete confirmation if this is the contact being deleted
        if st.session_state.show_delete_confirm and st.session_state.delete_contact_id == contact[7]:
            confirm_col1, confirm_col2, confirm_col3 = st.columns([2,1,1])
            with confirm_col1:
                st.warning("Delete this contact?")
            with confirm_col2:
                if st.button("Yes", key=f"confirm_delete_{contact[7]}", type="primary"):
                    if delete_contact(contact[7]):
                        st.session_state.delete_contact_id = None
                        st.session_state.show_delete_confirm = False
                        get_contacts.clear()
                        st.rerun()
            with confirm_col3:
                if st.button("No", key=f"cancel_delete_{contact[7]}"):
                    st.session_state.delete_contact_id = None
                    st.session_state.show_delete_confirm = False
                    st.rerun()
            return  # Skip showing the contact while confirming delete

        # Two-column layout: Info | Actions
        info_col, action_col = st.columns([6, 1])
        
        with info_col:
            # Name - using text() for smaller size
            if contact[1]:
                st.text(contact[1])
            # Contact details - all using text() for consistency
            if contact[2]:
                st.text(f"📞 {contact[2]}")
            if contact[3]:
                st.text(f"✉️ {contact[3]}")
            if contact[4]:
                st.text(f"📠 {contact[4]}")
            if contact[5] or contact[6]:
                st.text(f"📍 {contact[5] or contact[6]}")
        
        with action_col:
            # Action buttons stacked vertically, right-aligned
            if st.button("✏️", key=f"edit_{contact[7]}", help="Edit contact"):
                # Set up edit mode
                st.session_state.contact_form['mode'] = 'edit'
                ContactFormState.set_open(True)
                st.session_state.contact_form['contact_type'] = contact[0]
                st.session_state.contact_form['contact_id'] = contact[7]
                st.session_state.contact_form['form_data'] = {
                    'contact_name': contact[1] or '',
                    'phone': contact[2] or '',
                    'email': contact[3] or '',
                    'fax': contact[4] or '',
                    'physical_address': contact[5] or '',
                    'mailing_address': contact[6] or ''
                }
                st.rerun()
            if st.button("🗑️", key=f"delete_{contact[7]}", help="Delete contact"):
                st.session_state.delete_contact_id = contact[7]
                st.session_state.show_delete_confirm = True
                st.rerun()
        
        # Minimal separator
        st.divider()

def render_contact_section(contact_type, contacts):
    """Render a contact section with its contacts and add button"""
    with st.expander(f"{contact_type} Contact ({len(contacts)})", expanded=False):
        if contacts:
            for contact in contacts:
                render_contact_card(contact)
        else:
            st.caption(f"No {contact_type.lower()} contacts")
        
        if st.button(f"Add {contact_type} Contact", key=f"add_{contact_type.lower()}", use_container_width=True):
            ContactFormState.set_open(True)
            st.session_state.contact_form['contact_type'] = contact_type
            st.rerun() 