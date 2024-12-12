import streamlit as st
from utils.utils import (
    get_contacts, add_contact, format_phone_number_ui, format_phone_number_db,
    validate_phone_number, delete_contact, update_contact, get_clients
)

def init_contact_form_state():
    """Single source of truth for contact form state initialization.
    This function is the ONLY place where contact form state should be initialized.
    """
    if 'contact_form' not in st.session_state:
        st.session_state.contact_form = {
            'is_open': False,  # Keep for backward compatibility
            'visible': False,  # New standardized property
            'mode': 'add',  # 'add' or 'edit'
            'contact_type': None,
            'contact_id': None,  # Used for edit mode
            'has_validation_error': False,
            'show_cancel_confirm': False,
            'explicit_open': False,  # Track if form was explicitly opened
            'form_data': {
                'contact_name': '',
                'phone': '',
                'fax': '',
                'email': '',
                'physical_address': '',
                'mailing_address': ''
            }
        }
        st.session_state.delete_contact_id = None
        st.session_state.show_delete_confirm = False

def open_contact_form(contact_type=None, mode='add', contact_data=None):
    """Explicitly open the contact form with the given parameters."""
    if 'contact_form' not in st.session_state:
        init_contact_form_state()
    
    st.session_state.contact_form.update({
        'is_open': True,  # Keep for backward compatibility
        'visible': True,  # New standardized property
        'explicit_open': True,  # Mark as explicitly opened
        'mode': mode,
        'contact_type': contact_type,
        'contact_id': contact_data.get('contact_id') if contact_data else None,
        'has_validation_error': False,
        'show_cancel_confirm': False,
        'form_data': {
            'contact_name': contact_data.get('contact_name', '') if contact_data else '',
            'phone': contact_data.get('phone', '') if contact_data else '',
            'fax': contact_data.get('fax', '') if contact_data else '',
            'email': contact_data.get('email', '') if contact_data else '',
            'physical_address': contact_data.get('physical_address', '') if contact_data else '',
            'mailing_address': contact_data.get('mailing_address', '') if contact_data else ''
        }
    })

def clear_contact_form():
    """Clear contact form state completely."""
    if 'contact_form' in st.session_state:
        st.session_state.contact_form.update({
            'is_open': False,  # Keep for backward compatibility
            'visible': False,  # New standardized property
            'mode': 'add',
            'contact_type': None,
            'contact_id': None,
            'has_validation_error': False,
            'show_cancel_confirm': False,
            'explicit_open': False,
            'form_data': {
                'contact_name': '',
                'phone': '',
                'fax': '',
                'email': '',
                'physical_address': '',
                'mailing_address': ''
            }
        })
        # Clear the contacts cache to force a refresh
        get_contacts.clear()

def validate_form_data(form_data):
    """Check if at least one field has data"""
    return any(value.strip() for value in form_data.values())

def has_unsaved_changes(form_data):
    """Check if any field has data entered"""
    return any(value.strip() for value in form_data.values())

def clear_validation_error():
    """Clear the validation error state"""
    st.session_state.contact_form['has_validation_error'] = False

def format_phone_on_change():
    """Format phone number as user types"""
    clear_validation_error()
    key = f"phone_{st.session_state.contact_form['contact_type']}"
    if key in st.session_state:
        st.session_state.contact_form['form_data']['phone'] = format_phone_number_ui(st.session_state[key])

def format_fax_on_change():
    """Format fax number as user types"""
    clear_validation_error()
    key = f"fax_{st.session_state.contact_form['contact_type']}"
    if key in st.session_state:
        st.session_state.contact_form['form_data']['fax'] = format_phone_number_ui(st.session_state[key])

@st.dialog('Contact Form')
def show_contact_form():
    """Display and handle the contact form dialog."""
    if not st.session_state.contact_form['is_open']:
        return
    
    mode = st.session_state.contact_form['mode']
    action = "Edit" if mode == "edit" else "Add"
    
    st.subheader(f"{action} {st.session_state.contact_form['contact_type']} Contact")
    
    # Contact form fields
    contact_name = st.text_input(
        "Name",
        key=f"contact_name_{st.session_state.contact_form['contact_type']}",
        value=st.session_state.contact_form['form_data']['contact_name'],
        on_change=clear_validation_error
    )
    
    # Phone input with live formatting
    phone_input = st.text_input(
        "Phone",
        key=f"phone_{st.session_state.contact_form['contact_type']}",
        value=st.session_state.contact_form['form_data']['phone'],
        on_change=format_phone_on_change,
        placeholder="5555555555"
    )
    
    # Fax input with live formatting
    fax_input = st.text_input(
        "Fax",
        key=f"fax_{st.session_state.contact_form['contact_type']}",
        value=st.session_state.contact_form['form_data']['fax'],
        on_change=format_fax_on_change,
        placeholder="5555555555"
    )
    
    email = st.text_input(
        "Email",
        key=f"email_{st.session_state.contact_form['contact_type']}",
        value=st.session_state.contact_form['form_data']['email'],
        on_change=clear_validation_error
    )

    physical_address = st.text_area(
        "Physical Address",
        key=f"physical_address_{st.session_state.contact_form['contact_type']}",
        value=st.session_state.contact_form['form_data']['physical_address'],
        on_change=clear_validation_error
    )
    
    mailing_address = st.text_area(
        "Mailing Address",
        key=f"mailing_address_{st.session_state.contact_form['contact_type']}",
        value=st.session_state.contact_form['form_data']['mailing_address'],
        on_change=clear_validation_error
    )
    
    # Format phone numbers for database storage
    phone_db = format_phone_number_db(phone_input)
    fax_db = format_phone_number_db(fax_input)
    
    # Validate phone numbers
    if phone_input and not validate_phone_number(phone_input):
        st.error("Please enter a valid 10-digit phone number")
        return
    
    if fax_input and not validate_phone_number(fax_input):
        st.error("Please enter a valid 10-digit fax number")
        return
    
    # Capture form data
    form_data = {
        'contact_name': contact_name,
        'phone': phone_db,
        'fax': fax_db,
        'email': email,
        'physical_address': physical_address,
        'mailing_address': mailing_address
    }
    
    # Show validation error if present
    if st.session_state.contact_form['has_validation_error']:
        st.error("Please fill in at least one field.")
    
    # Show cancel confirmation if needed
    if st.session_state.contact_form['show_cancel_confirm']:
        st.warning("You have unsaved changes. Are you sure you want to cancel?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes, Discard Changes", type="primary", use_container_width=True):
                clear_contact_form()
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
                if validate_form_data(form_data):
                    # Get client_id from session state
                    client_id = next(
                        client[0] for client in get_clients()
                        if client[1] == st.session_state.client_selector_dashboard
                    )
                    
                    if mode == "edit":
                        if update_contact(st.session_state.contact_form['contact_id'], form_data):
                            clear_contact_form()
                            get_contacts.clear()
                            st.rerun()
                    else:
                        if add_contact(
                            client_id,
                            st.session_state.contact_form['contact_type'],
                            form_data
                        ):
                            clear_contact_form()
                            get_contacts.clear()
                            st.rerun()
                else:
                    st.session_state.contact_form['has_validation_error'] = True
                    st.rerun()
        
        with col2:
            if st.button("Cancel", use_container_width=True):
                if has_unsaved_changes(form_data):
                    st.session_state.contact_form['show_cancel_confirm'] = True
                    st.rerun()
                else:
                    clear_contact_form()
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
                # Set up edit mode using the new form management
                contact_data = {
                    'contact_id': contact[7],
                    'contact_name': contact[1],
                    'phone': contact[2],
                    'email': contact[3],
                    'fax': contact[4],
                    'physical_address': contact[5],
                    'mailing_address': contact[6]
                }
                open_contact_form(
                    contact_type=contact[0],
                    mode='edit',
                    contact_data=contact_data
                )
                st.rerun()
            if st.button("🗑️", key=f"delete_{contact[7]}", help="Delete contact"):
                st.session_state.delete_contact_id = contact[7]
                st.session_state.show_delete_confirm = True
                st.rerun()
        
        # Minimal separator
        st.divider()

def render_contact_section(contact_type, contacts, ui_manager=None):
    """Render a contact section with its contacts and add button"""
    with st.expander(f"{contact_type} Contact ({len(contacts)})", expanded=False):
        if contacts:
            for contact in contacts:
                render_contact_card(contact)
        else:
            st.caption(f"No {contact_type.lower()} contacts")
        
        if st.button(f"Add {contact_type} Contact", key=f"add_{contact_type.lower()}", use_container_width=True):
            if ui_manager:
                ui_manager.show_contact_form()
                st.session_state.contact_form['contact_type'] = contact_type
            else:
                open_contact_form(contact_type=contact_type)
            st.rerun() 