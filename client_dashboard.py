# client_dashboard.py
import streamlit as st
import pandas as pd
import time
from datetime import datetime
from utils import (
    get_clients, get_client_details, get_active_contract, 
    get_latest_payment, get_contacts, get_payment_history,
    calculate_rate_conversions, update_payment_note, add_contact,
    format_phone_number_ui, format_phone_number_db, validate_phone_number,
    delete_contact, update_contact
)

# Contact form state management
def init_contact_form_state():
    if 'contact_form' not in st.session_state:
        st.session_state.contact_form = {
            'is_open': False,
            'mode': 'add',  # 'add' or 'edit'
            'contact_type': None,
            'contact_id': None,  # Used for edit mode
            'has_validation_error': False,
            'show_cancel_confirm': False,
            'form_data': {
                'contact_name': '',
                'phone': '',
                'fax': '',
                'email': '',
                'physical_address': '',
                'mailing_address': ''
            }
        }
    if 'delete_contact_id' not in st.session_state:
        st.session_state.delete_contact_id = None
    if 'show_delete_confirm' not in st.session_state:
        st.session_state.show_delete_confirm = False

def clear_form():
    if 'contact_form' in st.session_state:
        st.session_state.contact_form['form_data'] = {
            'contact_name': '',
            'phone': '',
            'fax': '',
            'email': '',
            'physical_address': '',
            'mailing_address': ''
        }
        st.session_state.contact_form['is_open'] = False
        st.session_state.contact_form['has_validation_error'] = False
        st.session_state.contact_form['show_cancel_confirm'] = False
        
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
                print("\n❌ Form cancelled - changes discarded")
                clear_form()
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
                        # Update existing contact
                        if update_contact(st.session_state.contact_form['contact_id'], form_data):
                            print(f"\n✅ Successfully updated {st.session_state.contact_form['contact_type']} contact in database:")
                            for field, value in form_data.items():
                                print(f"  {field}: {value}")
                            clear_form()
                            get_contacts.clear()  # Clear the contacts cache
                            st.rerun()
                    else:
                        # Add new contact
                        contact_id = add_contact(
                            client_id,
                            st.session_state.contact_form['contact_type'],
                            form_data
                        )
                        
                        if contact_id:
                            print(f"\n✅ Successfully added {st.session_state.contact_form['contact_type']} contact to database:")
                            for field, value in form_data.items():
                                print(f"  {field}: {value}")
                            clear_form()
                            get_contacts.clear()  # Clear the contacts cache
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
                    print("\n❌ Form cancelled - no changes to discard")
                    clear_form()
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
                st.session_state.contact_form['is_open'] = True
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

def show_client_dashboard():
    st.write("👥 Client Dashboard")
    
    # Initialize contact form state
    init_contact_form_state()
    
    # Show contact form dialog if open
    if 'contact_form' in st.session_state and st.session_state.contact_form['is_open']:
        show_contact_form()
    
    # Client selector in a compact container
    clients = get_clients()
    client_options = ["Select a client..."] + [client[1] for client in clients]
    selected_client_name = st.selectbox(
        "🔍 Search or select a client",
        options=client_options,
        key="client_selector_dashboard",
        label_visibility="collapsed"
    )
    
    if selected_client_name != "Select a client...":

        
        client_id = next(
            client[0] for client in clients if client[1] == selected_client_name
        )
        
        # Get all required data
        client_details = get_client_details(client_id)
        contacts = get_contacts(client_id)
        
        # Create three equal-width columns for contact cards
        c1, c2, c3 = st.columns(3)
        
        contact_types = {'Primary': [], 'Authorized': [], 'Provider': []}
        
        if contacts:
            for contact in contacts:
                if contact[0] in contact_types:
                    contact_types[contact[0]].append(contact)
        
        # Primary Contacts Card
        with c1:
            with st.expander(f"Primary Contact ({len(contact_types['Primary'])})", expanded=False):
                if contact_types['Primary']:
                    for contact in contact_types['Primary']:
                        render_contact_card(contact)
                    if st.button("Add Primary Contact", key="add_primary", use_container_width=True):
                        st.session_state.contact_form['is_open'] = True
                        st.session_state.contact_form['contact_type'] = 'Primary'
                        st.rerun()
                else:
                    st.caption("No primary contacts")
                    if st.button("Add Primary Contact", key="add_primary", use_container_width=True):
                        st.session_state.contact_form['is_open'] = True
                        st.session_state.contact_form['contact_type'] = 'Primary'
                        st.rerun()
        
        # Authorized Contacts Card
        with c2:
            with st.expander(f"Authorized Contact ({len(contact_types['Authorized'])})", expanded=False):
                if contact_types['Authorized']:
                    for contact in contact_types['Authorized']:
                        render_contact_card(contact)
                    if st.button("Add Authorized Contact", key="add_authorized", use_container_width=True):
                        st.session_state.contact_form['is_open'] = True
                        st.session_state.contact_form['contact_type'] = 'Authorized'
                        st.rerun()
                else:
                    st.caption("No authorized contacts")
                    if st.button("Add Authorized Contact", key="add_authorized", use_container_width=True):
                        st.session_state.contact_form['is_open'] = True
                        st.session_state.contact_form['contact_type'] = 'Authorized'
                        st.rerun()
        
        # Provider Contacts Card
        with c3:
            with st.expander(f"Provider Contact ({len(contact_types['Provider'])})", expanded=False):
                if contact_types['Provider']:
                    for contact in contact_types['Provider']:
                        render_contact_card(contact)
                    if st.button("Add Provider Contact", key="add_provider", use_container_width=True):
                        st.session_state.contact_form['is_open'] = True
                        st.session_state.contact_form['contact_type'] = 'Provider'
                        st.rerun()
                else:
                    st.caption("No provider contacts")
                    if st.button("Add Provider Contact", key="add_provider", use_container_width=True):
                        st.session_state.contact_form['is_open'] = True
                        st.session_state.contact_form['contact_type'] = 'Provider'
                        st.rerun()
        
        # Payments History Section
        st.markdown("<div style='margin: 2rem 0 1rem 0;'></div>", unsafe_allow_html=True)
        st.markdown("### Payment History")
        
        payments = get_payment_history(client_id)
        
        if not payments:
            st.info("No payment history available for this client.", icon="ℹ️")
        else:
            # Create a list to store the formatted data
            table_data = []
            
            for payment in payments:
                provider_name = payment[0] or "N/A"
                
                # Format currency values
                def format_currency(value):
                    try:
                        if value is None or value == "":
                            return "N/A"
                        return f"${float(value):,.2f}"
                    except (ValueError, TypeError):
                        return "N/A"
                
                # Format payment period
                if payment[1] == payment[3] and payment[2] == payment[4]:
                    period = f"Q{payment[1]} {payment[2]}"
                else:
                    period = f"Q{payment[1]} {payment[2]} - Q{payment[3]} {payment[4]}"
                
                frequency = payment[5].title() if payment[5] else "N/A"
                
                # Format date
                received_date = "N/A"
                if payment[6]:
                    try:
                        date_obj = datetime.strptime(payment[6], '%Y-%m-%d')
                        received_date = date_obj.strftime('%b %d, %Y')
                    except:
                        received_date = payment[6]
                
                # Format all currency values using the helper function
                total_assets = format_currency(payment[7])
                expected_fee = format_currency(payment[8])
                actual_fee = format_currency(payment[9])
                
                # Calculate fee discrepancy
                try:
                    if payment[8] is not None and payment[9] is not None and payment[8] != "" and payment[9] != "":
                        discrepancy = float(payment[9]) - float(payment[8])
                        discrepancy_str = f"${discrepancy:,.2f}" if discrepancy >= 0 else f"-${abs(discrepancy):,.2f}"
                    else:
                        discrepancy_str = "N/A"
                except (ValueError, TypeError):
                    discrepancy_str = "N/A"
                
                # Notes with edit functionality
                notes = payment[10] or ""
                payment_id = payment[11]
                
                table_data.append({
                    "Provider": provider_name,
                    "Period": period,
                    "Frequency": frequency,
                    "Received": received_date,
                    "Total Assets": total_assets,
                    "Expected Fee": expected_fee,
                    "Actual Fee": actual_fee,
                    "Discrepancy": discrepancy_str,
                    "Notes": notes,
                    "payment_id": payment_id
                })
            
            # Create DataFrame for the table
            df = pd.DataFrame(table_data)
            
            # Function to handle note updates
            def handle_note_edit(payment_id, new_note):
                update_payment_note(payment_id, new_note)
                # Clear the active note state
                if 'active_note_payment_id' in st.session_state:
                    del st.session_state.active_note_payment_id
                st.rerun()
            
            def render_note_cell(payment_id, note):
                # Initialize session state for this note's popup if not exists
                if f"show_note_popup_{payment_id}" not in st.session_state:
                    st.session_state[f"show_note_popup_{payment_id}"] = False
                
                has_note = bool(note)
                icon_content = "🟢" if has_note else "◯"
                
                # Create the note button with tooltip
                if st.button(
                    icon_content, 
                    key=f"note_button_{payment_id}",
                    help=note if has_note else "Add note",
                    use_container_width=False
                ):
                    # Auto-save if there's an active note and we're switching to a different one
                    if 'active_note_payment_id' in st.session_state:
                        active_id = st.session_state.active_note_payment_id
                        if active_id != payment_id and f"note_textarea_{active_id}" in st.session_state:
                            handle_note_edit(active_id, st.session_state[f"note_textarea_{active_id}"])
                    
                    # Toggle the note form
                    if 'active_note_payment_id' in st.session_state and st.session_state.active_note_payment_id == payment_id:
                        # Auto-save on toggle off
                        if f"note_textarea_{payment_id}" in st.session_state:
                            handle_note_edit(payment_id, st.session_state[f"note_textarea_{payment_id}"])
                        del st.session_state.active_note_payment_id
                    else:
                        st.session_state.active_note_payment_id = payment_id
                    st.rerun()                
                # Style the button
                st.markdown(f"""
                    <style>
                        [data-testid="baseButton-secondary"]:has(div[key="note_button_{payment_id}"]) {{
                            width: 32px !important;
                            height: 32px !important;
                            padding: 0 !important;
                            border-radius: 50% !important;
                            display: flex !important;
                            align-items: center !important;
                            justify-content: center !important;
                            background: transparent !important;
                            border: {has_note and "none" or "2px dashed #ccc"} !important;
                            color: {has_note and "#1f77b4" or "#ccc"} !important;
                            margin: 0 auto !important;
                        }}
                    </style>
                """, unsafe_allow_html=True)
            
            # Create a container for the full-width note form
            note_form_container = st.container()
            
            # Display column headers
            header_cols = st.columns([2, 2, 1, 2, 2, 2, 2, 2, 1])
            with header_cols[0]:
                st.markdown('<p class="payment-header">Provider</p>', unsafe_allow_html=True)
            with header_cols[1]:
                st.markdown('<p class="payment-header">Period</p>', unsafe_allow_html=True)
            with header_cols[2]:
                st.markdown('<p class="payment-header">Frequency</p>', unsafe_allow_html=True)
            with header_cols[3]:
                st.markdown('<p class="payment-header">Received</p>', unsafe_allow_html=True)
            with header_cols[4]:
                st.markdown('<p class="payment-header">Total Assets</p>', unsafe_allow_html=True)
            with header_cols[5]:
                st.markdown('<p class="payment-header">Expected Fee</p>', unsafe_allow_html=True)
            with header_cols[6]:
                st.markdown('<p class="payment-header">Actual Fee</p>', unsafe_allow_html=True)
            with header_cols[7]:
                st.markdown('<p class="payment-header">Discrepancy</p>', unsafe_allow_html=True)
            with header_cols[8]:
                st.markdown('<p class="payment-header">Notes</p>', unsafe_allow_html=True)
            
            # Display each row with note icons
            for index, row in df.iterrows():
                row_container = st.container()
                with row_container:
                    cols = st.columns([2, 2, 1, 2, 2, 2, 2, 2, 1])
                    
                    with cols[0]:
                        st.write(row["Provider"])
                    with cols[1]:
                        st.write(row["Period"])
                    with cols[2]:
                        st.write(row["Frequency"])
                    with cols[3]:
                        st.write(row["Received"])
                    with cols[4]:
                        st.write(row["Total Assets"])
                    with cols[5]:
                        st.write(row["Expected Fee"])
                    with cols[6]:
                        st.write(row["Actual Fee"])
                    with cols[7]:
                        st.write(row["Discrepancy"])
                    with cols[8]:
                        render_note_cell(row["payment_id"], row["Notes"])
                    
                    # If this is the active note row, render the full-width form
                    if (
                        'active_note_payment_id' in st.session_state 
                        and st.session_state.active_note_payment_id == row["payment_id"]
                    ):
                        with st.container():
                            # Create columns to position the note field
                            note_cols = st.columns([7, 9])  # 7 units for spacing, 9 for the note
                            
                            # Use the second column for the note
                            with note_cols[1]:
                                st.markdown(f"""<div style="border-top: 1px solid #eee; padding-top: 0.5rem;"></div>""", unsafe_allow_html=True)
                                
                                # Note input starting from middle of table
                                st.text_area(
                                    f"Note for {row['Provider']} - {row['Period']}",
                                    value=row["Notes"] or "",
                                    key=f"note_textarea_{row['payment_id']}",
                                    height=100,
                                    placeholder="Enter note here..."
                                )

