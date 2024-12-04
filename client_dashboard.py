# client_dashboard.py
import streamlit as st
import pandas as pd
import time
from datetime import datetime
from utils import (
    get_clients, get_client_details, get_active_contract, 
    get_latest_payment, get_contacts, get_payment_history,
    calculate_rate_conversions, update_payment_note, add_contact,
    format_phone_number_ui, format_phone_number_db, validate_phone_number
)

def init_contact_state():
    """Initialize contact form state"""
    if 'contact_state' not in st.session_state:
        reset_contact_state()

def reset_contact_state():
    """Reset contact form state"""
    st.session_state.contact_state = {
        'show_dialog': False,
        'client_id': None,
        'contact_type': None,
        'form_data': {
            'name': '',
            'phone': '',
            'fax': '',
            'email': '',
            'physical_address': '',
            'mailing_address': ''
        },
        'show_confirm': False,
        'pending_action': None  # Track pending state changes
    }

def update_contact_state(**kwargs):
    """Atomic update of contact state"""
    if 'contact_state' not in st.session_state:
        init_contact_state()
    st.session_state.contact_state.update(kwargs)

def has_form_data():
    """Check if any field has data"""
    return any(
        value.strip() 
        for value in st.session_state.contact_state['form_data'].values()
    )

@st.dialog("Add Contact")
def contact_modal():
    """Display the contact form modal"""
    # Only show if explicitly enabled
    if not st.session_state.contact_state['show_dialog']:
        return False
    
    # Handle any pending actions
    if st.session_state.contact_state.get('pending_action') == 'close':
        reset_contact_state()
        st.rerun()
        return False
    
    st.subheader(f"Add {st.session_state.contact_state['contact_type']}")

    # Form fields with state persistence
    name = st.text_input(
        "Name",
        value=st.session_state.contact_state['form_data']['name']
    )
    
    # Phone with formatting
    phone_input = st.text_input(
        "Phone",
        value=st.session_state.contact_state['form_data']['phone'],
        help="Enter 10 digits for automatic formatting"
    )
    phone = format_phone_number_ui(phone_input) if phone_input else ""
        
    # Fax with formatting
    fax_input = st.text_input(
        "Fax",
        value=st.session_state.contact_state['form_data']['fax'],
        help="Enter 10 digits for automatic formatting"
    )
    fax = format_phone_number_ui(fax_input) if fax_input else ""
        
    email = st.text_input(
        "Email",
        value=st.session_state.contact_state['form_data']['email']
    )
    physical_address = st.text_area(
        "Physical Address",
        value=st.session_state.contact_state['form_data']['physical_address']
    )
    mailing_address = st.text_area(
        "Mailing Address",
        value=st.session_state.contact_state['form_data']['mailing_address']
    )

    # Update form data
    st.session_state.contact_state['form_data'].update({
        'name': name,
        'phone': phone,
        'fax': fax,
        'email': email,
        'physical_address': physical_address,
        'mailing_address': mailing_address
    })

    # Action buttons
    col1, col2 = st.columns([1, 1])
    
    # Save button
    with col1:
        if st.button("Save", type="primary", use_container_width=True):
            # Validate phone/fax if provided
            if phone and not validate_phone_number(phone):
                st.error("Please enter a valid 10-digit phone number.")
                return True
            if fax and not validate_phone_number(fax):
                st.error("Please enter a valid 10-digit fax number.")
                return True

            # Check if any field is filled
            if not has_form_data():
                st.error("Please fill in at least one field.")
                return True

            try:
                # Format data for database
                form_data = {
                    'contact_name': name,
                    'phone': format_phone_number_db(phone) if phone else '',
                    'email': email,
                    'fax': format_phone_number_db(fax) if fax else '',
                    'physical_address': physical_address,
                    'mailing_address': mailing_address
                }

                # Add to database
                add_contact(
                    st.session_state.contact_state['client_id'],
                    st.session_state.contact_state['contact_type'],
                    form_data
                )
                st.success(f"{st.session_state.contact_state['contact_type']} added successfully!")
                time.sleep(1)
                reset_contact_state()
                st.rerun()

            except Exception as e:
                st.error(f"Error saving contact: {str(e)}")
                return True

    # Cancel button
    with col2:
        if st.button("Cancel", use_container_width=True):
            if has_form_data() and not st.session_state.contact_state['show_confirm']:
                update_contact_state(show_confirm=True)
                st.warning("Are you sure? All entered data will be lost.")
                col3, col4 = st.columns([1, 1])
                with col3:
                    if st.button("Yes, Cancel", key="confirm_yes", use_container_width=True):
                        update_contact_state(pending_action='close')
                        st.rerun()
                with col4:
                    if st.button("No, Continue", key="confirm_no", use_container_width=True):
                        update_contact_state(show_confirm=False)
                        st.rerun()
            else:
                update_contact_state(pending_action='close')
                st.rerun()
    
    return True

def show_client_dashboard():
    """Render the client dashboard page"""
    # Initialize session state for modal management
    if 'active_modal' not in st.session_state:
        st.session_state.active_modal = None
    if 'modal_data' not in st.session_state:
        st.session_state.modal_data = {
            'client_id': None,
            'contact_type': None,
            'show_confirm': False,
            'fields': {
                'name': '',
                'phone': '',
                'fax': '',
                'email': '',
                'physical_address': '',
                'mailing_address': ''
            }
        }
    
    st.write("👥 Client Dashboard")
    
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
        # Reset form state when client changes
        if ('selected_client' not in st.session_state or 
            st.session_state.selected_client != selected_client_name):
            st.session_state.selected_client = selected_client_name
            reset_contact_state()
        
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
                        st.markdown(f"""
                        <div class="contact-info">
                            <div class="contact-name">{contact[1] if contact[1] else ''}</div>
                            <div class="contact-detail">📞 {contact[2] if contact[2] else 'No phone'}</div>
                            <div class="contact-detail">✉️ {contact[3] if contact[3] else 'No email'}</div>
                            {'<div class="contact-detail">📍 ' + (contact[5] or contact[6]) + '</div>' if (contact[5] or contact[6]) else ''}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.write("No primary contacts")
                
                # Add Contact button
                if st.button("Add Primary Contact", key="add_primary", use_container_width=True):
                    # Reset any existing state first
                    reset_contact_state()
                    # Then set new state
                    update_contact_state(
                        show_dialog=True,
                        client_id=client_id,
                        contact_type="Primary Contact"
                    )
                    st.rerun()
        
        # Authorized Contacts Card
        with c2:
            with st.expander(f"Authorized Contact ({len(contact_types['Authorized'])})", expanded=False):
                if contact_types['Authorized']:
                    for contact in contact_types['Authorized']:
                        st.markdown(f"""
                        <div class="contact-info">
                            <div class="contact-name">{contact[1] if contact[1] else ''}</div>
                            <div class="contact-detail">📞 {contact[2] if contact[2] else 'No phone'}</div>
                            <div class="contact-detail">✉️ {contact[3] if contact[3] else 'No email'}</div>
                            {'<div class="contact-detail">📍 ' + (contact[5] or contact[6]) + '</div>' if (contact[5] or contact[6]) else ''}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.write("No authorized contacts")
                
                # Add Contact button
                if st.button("Add Authorized Contact", key="add_authorized", use_container_width=True):
                    # Reset any existing state first
                    reset_contact_state()
                    # Then set new state
                    update_contact_state(
                        show_dialog=True,
                        client_id=client_id,
                        contact_type="Authorized Contact"
                    )
                    st.rerun()
        
        # Provider Contacts Card
        with c3:
            with st.expander(f"Provider Contact ({len(contact_types['Provider'])})", expanded=False):
                if contact_types['Provider']:
                    for contact in contact_types['Provider']:
                        st.markdown(f"""
                        <div class="contact-info">
                            <div class="contact-name">{contact[1] if contact[1] else ''}</div>
                            <div class="contact-detail">📞 {contact[2] if contact[2] else 'No phone'}</div>
                            <div class="contact-detail">✉️ {contact[3] if contact[3] else 'No email'}</div>
                            {'<div class="contact-detail">📍 ' + (contact[5] or contact[6]) + '</div>' if (contact[5] or contact[6]) else ''}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.write("No provider contacts")
                
                # Add Contact button
                if st.button("Add Provider Contact", key="add_provider", use_container_width=True):
                    # Reset any existing state first
                    reset_contact_state()
                    # Then set new state
                    update_contact_state(
                        show_dialog=True,
                        client_id=client_id,
                        contact_type="Provider Contact"
                    )
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

