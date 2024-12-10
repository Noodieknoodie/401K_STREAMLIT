import streamlit as st
import pandas as pd
from datetime import datetime
from utils.utils import (
    get_payment_history, update_payment_note,
    get_paginated_payment_history, get_total_payment_count,
    get_payment_year_quarters, get_clients, get_contacts,
    get_client_details, add_contact, update_contact,
    delete_contact
)
from utils.perf_logging import log_event

# ============================================================================
# CONTACT FORM STATE MANAGEMENT
# ============================================================================

def init_contact_form_state():
    """Initialize contact form state management."""
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

def clear_contact_form():
    """Clear the contact form state."""
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
        get_contacts.clear()  # Clear the contacts cache

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
        value=st.session_state.contact_form['form_data']['contact_name']
    )
    
    phone = st.text_input(
        "Phone",
        key=f"phone_{st.session_state.contact_form['contact_type']}",
        value=st.session_state.contact_form['form_data']['phone'],
        placeholder="5555555555"
    )
    
    fax = st.text_input(
        "Fax",
        key=f"fax_{st.session_state.contact_form['contact_type']}",
        value=st.session_state.contact_form['form_data']['fax'],
        placeholder="5555555555"
    )
    
    email = st.text_input(
        "Email",
        key=f"email_{st.session_state.contact_form['contact_type']}",
        value=st.session_state.contact_form['form_data']['email']
    )
    
    physical_address = st.text_area(
        "Physical Address",
        key=f"physical_address_{st.session_state.contact_form['contact_type']}",
        value=st.session_state.contact_form['form_data']['physical_address']
    )
    
    mailing_address = st.text_area(
        "Mailing Address",
        key=f"mailing_address_{st.session_state.contact_form['contact_type']}",
        value=st.session_state.contact_form['form_data']['mailing_address']
    )
    
    # Form validation and submission
    form_data = {
        'contact_name': contact_name,
        'phone': phone,
        'fax': fax,
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
                if any(value.strip() for value in form_data.values()):
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
                if any(value.strip() for value in form_data.values()):
                    st.session_state.contact_form['show_cancel_confirm'] = True
                    st.rerun()
                else:
                    clear_contact_form()
                    st.rerun()

# ============================================================================
# STATE MANAGEMENT INITIALIZATION FUNCTIONS
# ============================================================================

def init_payment_form_state():
    """Initialize payment form state management.
    BEFORE: State was initialized in main flow, causing reset on every reload
    AFTER: Centralized initialization function, only runs when state doesn't exist
    """
    if 'payment_form' not in st.session_state:
        current_quarter = (datetime.now().month - 1) // 3 + 1
        current_year = datetime.now().year
        prev_quarter = current_quarter - 1 if current_quarter > 1 else 4
        prev_year = current_year if current_quarter > 1 else current_year - 1
        
        st.session_state.payment_form = {
            'is_visible': False,  # Dedicated state for visibility
            'client_id': None,    # Track which client the form belongs to
            'mode': 'add',
            'has_validation_error': False,
            'show_cancel_confirm': False,
            'modal_lock': False,
            'form_data': {
                'received_date': datetime.now().strftime('%Y-%m-%d'),
                'applied_start_quarter': prev_quarter,
                'applied_start_year': prev_year,
                'applied_end_quarter': None,
                'applied_end_year': None,
                'total_assets': '',
                'actual_fee': '',
                'expected_fee': None,
                'method': 'None Specified',
                'other_method': '',
                'notes': ''
            }
        }
    elif 'client_id' not in st.session_state.payment_form:
        # Add client_id to existing payment form states
        st.session_state.payment_form['client_id'] = None

def init_notes_state():
    """Initialize centralized notes state management.
    BEFORE: Multiple scattered state keys for notes
    AFTER: Single consolidated notes state object
    """
    if 'notes_state' not in st.session_state:
        st.session_state.notes_state = {
            'active_note': None,
            'edited_notes': {},
            'temp_notes': {}  # For storing unsaved changes
        }

def init_filter_state():
    """Initialize payment filter state management.
    BEFORE: Individual state keys for filters
    AFTER: Bundled filter state in single object
    """
    if 'filter_state' not in st.session_state:
        st.session_state.filter_state = {
            'year': None,
            'quarter': None,
            'current_filters': None  # Tuple of (year_filters, quarter_filters)
        }

def clear_client_specific_states():
    """Clear all client-specific states when switching clients.
    BEFORE: Incomplete state cleanup on client switch
    AFTER: Comprehensive cleanup of all client-related states
    """
    # Clear payment data
    st.session_state.payment_data = []
    st.session_state.payment_offset = 0
    
    # Clear filter state
    if 'filter_state' in st.session_state:
        st.session_state.filter_state = {
            'year': None,
            'quarter': None,
            'current_filters': None
        }
    
    # Clear notes state
    if 'notes_state' in st.session_state:
        st.session_state.notes_state = {
            'active_note': None,
            'edited_notes': {},
            'temp_notes': {}
        }
    
    # Reset payment form - Updated to include client_id reset
    if 'payment_form' in st.session_state:
        st.session_state.payment_form['is_visible'] = False
        st.session_state.payment_form['client_id'] = None  # Reset client association
        st.session_state.payment_form['mode'] = 'add'
        st.session_state.payment_form['has_validation_error'] = False
        st.session_state.payment_form['show_cancel_confirm'] = False
        st.session_state.payment_form['modal_lock'] = False
        st.session_state.payment_form['form_data'] = {
            'received_date': datetime.now().strftime('%Y-%m-%d'),
            'applied_start_quarter': (datetime.now().month - 1) // 3 + 1,
            'applied_start_year': datetime.now().year,
            'applied_end_quarter': None,
            'applied_end_year': None,
            'total_assets': '',
            'actual_fee': '',
            'expected_fee': None,
            'method': 'None Specified',
            'other_method': '',
            'notes': ''
        }

def format_payment_data(payments):
    """Format payment data for display with consistent formatting."""
    table_data = []
    
    for payment in payments:
        provider_name = payment[0] or "N/A"
        
        def format_currency(value):
            try:
                if value is None or value == "":
                    return "N/A"
                return f"${float(value):,.2f}"
            except (ValueError, TypeError):
                return "N/A"
        
        # Format payment period based on frequency
        frequency = payment[5].title() if payment[5] else "N/A"
        
        if frequency.lower() == "monthly":
            # For monthly payments, convert quarter to month range
            start_month = ((payment[1] - 1) * 3) + 1
            end_month = ((payment[3] - 1) * 3) + 3
            
            if payment[2] == payment[4] and start_month == end_month:
                # Single month
                period = f"{datetime.strptime(f'2000-{start_month}-1', '%Y-%m-%d').strftime('%b')} {payment[2]}"
            else:
                # Month range
                start_date = datetime.strptime(f'2000-{start_month}-1', '%Y-%m-%d')
                end_date = datetime.strptime(f'2000-{end_month}-1', '%Y-%m-%d')
                if payment[2] == payment[4]:
                    period = f"{start_date.strftime('%b')} - {end_date.strftime('%b')} {payment[2]}"
                else:
                    period = f"{start_date.strftime('%b')} {payment[2]} - {end_date.strftime('%b')} {payment[4]}"
        else:
            # Quarterly payments
            if payment[1] == payment[3] and payment[2] == payment[4]:
                period = f"Q{payment[1]} {payment[2]}"
            else:
                period = f"Q{payment[1]} {payment[2]} - Q{payment[3]} {payment[4]}"
        
        # Format date
        received_date = "N/A"
        if payment[6]:
            try:
                date_obj = datetime.strptime(payment[6], '%Y-%m-%d')
                received_date = date_obj.strftime('%b %d, %Y')
            except:
                received_date = payment[6]
        
        # Format all currency values
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
    
    return table_data

def handle_note_edit(payment_id, new_note):
    """Handle updating a payment note."""
    log_event('note_saved', {'payment_id': payment_id, 'has_content': bool(new_note)})
    update_payment_note(payment_id, new_note)
    if 'notes_state' in st.session_state:
        st.session_state.notes_state['active_note'] = None

@st.cache_data(ttl=60)  # Cache note formatting for 1 minute
def format_note_display(note):
    """Format note for display with caching."""
    return bool(note), "🟢" if note else "◯", note if note else "Add note"

def initialize_notes_state():
    """Initialize centralized note state management."""
    if 'notes_state' not in st.session_state:
        st.session_state.notes_state = {
            'active_note': None,
            'edited_notes': {}
        }

def render_note_cell(payment_id, note, provider=None, period=None):
    """Render a note cell with edit functionality using centralized state."""
    initialize_notes_state()
    
    # Get cached note display format
    has_note = bool(note)
    icon_content = "🟢" if has_note else "◯"
    tooltip = note if has_note else "Add note"
    
    # Create unique key for this note
    note_key = f"note_{payment_id}"
    
    # Create clickable text with custom CSS and JavaScript
    st.markdown(f"""
        <style>
        .clickable-text {{
            cursor: pointer;
            color: #1E90FF;
            text-decoration: none;
        }}
        .clickable-text:hover {{
            text-decoration: underline;
        }}
        </style>
        <span 
            class="clickable-text" 
            title="{tooltip}" 
            onclick="handleNoteClick('{note_key}')" 
            id="{note_key}"
        >
            {icon_content}
        </span>
        <script>
        function handleNoteClick(key) {{
            Streamlit.setComponentValue(key, true);
        }}
        </script>
    """, unsafe_allow_html=True)
    
    # Check if the clickable text was clicked
    if st.session_state.get(note_key, False):
        notes_state = st.session_state.notes_state
        
        # Log note interaction
        log_event('note_clicked', {
            'payment_id': payment_id,
            'action': 'close' if notes_state['active_note'] == payment_id else 'open',
            'has_content': bool(note)
        })
        
        # Auto-save previous note if exists
        if notes_state['active_note'] and notes_state['active_note'] != payment_id:
            prev_id = notes_state['active_note']
            if prev_id in notes_state['edited_notes']:
                update_payment_note(prev_id, notes_state['edited_notes'][prev_id])
                notes_state['edited_notes'].pop(prev_id)
        
        # Toggle note state
        if notes_state['active_note'] == payment_id:
            if payment_id in notes_state['edited_notes']:
                update_payment_note(payment_id, notes_state['edited_notes'][payment_id])
                notes_state['edited_notes'].pop(payment_id)
            notes_state['active_note'] = None
        else:
            notes_state['active_note'] = payment_id
        
        # Reset the clicked state
        st.session_state[note_key] = False
        # Let Streamlit handle the rerun naturally
    
    # Note editing form
    if (
        'notes_state' in st.session_state 
        and st.session_state.notes_state['active_note'] == payment_id
    ):
        with st.container():
            note_cols = st.columns([7, 9])
            with note_cols[1]:
                st.markdown("""<div style="border-top: 1px solid #eee; padding-top: 0.5rem;"></div>""", unsafe_allow_html=True)
                edited_note = st.text_area(
                    f"Note for {provider or 'Payment'} - {period or 'Period'}",
                    value=note or "",
                    key=f"note_textarea_{payment_id}",
                    height=100,
                    placeholder="Enter note here..."
                )
                if edited_note != note:
                    st.session_state.notes_state['edited_notes'][payment_id] = edited_note
                    # Let Streamlit handle text_area updates naturally

def show_payment_history(client_id):
    """Display payment history with efficient layout and smart navigation."""
    
    # Initialize all required states
    init_payment_form_state()
    init_notes_state()
    init_filter_state()
    
    # Initialize payment state
    if 'payment_data' not in st.session_state:
        st.session_state.payment_data = []
    if 'payment_offset' not in st.session_state:
        st.session_state.payment_offset = 0
    
    # Get data first
    total_payments = get_total_payment_count(client_id)
    year_quarters = get_payment_year_quarters(client_id)
    
    # Get available years
    years = sorted(list(set(yq[0] for yq in year_quarters)), reverse=True)
    if not years:
        st.info("No payment history available.")
        return
    
    # Create a row with the same width as the table
    left_col, middle_col, right_col = st.columns([4, 2, 4])
    
    with left_col:
        time_filter = st.radio(
            "Time Period Filter",
            options=["All Time", "This Year", "Custom"],
            horizontal=True,
            label_visibility="collapsed"
        )
        
        if time_filter == "Custom":
            col1, col2, _ = st.columns([1, 1, 2])
            with col1:
                selected_year = st.selectbox(
                    "Select Year",
                    options=years,
                    index=0,
                    label_visibility="collapsed"
                )
                st.session_state.filter_state['year'] = selected_year
            with col2:
                selected_quarter = st.selectbox(
                    "Select Quarter",
                    options=["All Quarters", "Q1", "Q2", "Q3", "Q4"],
                    index=0,
                    label_visibility="collapsed"
                )
                st.session_state.filter_state['quarter'] = selected_quarter
    
    with middle_col:
        if st.button("Add Payment", type="primary", use_container_width=True):
            st.session_state.payment_form['is_visible'] = True  # Use dedicated visibility state
            st.rerun()
    
    with right_col:
        status_text = (
            f"Viewing all {total_payments} payments" if time_filter == "All Time" else
            f"Viewing payments from {datetime.now().year}" if time_filter == "This Year" else
            f"Viewing payments from {st.session_state.filter_state['year']}" + 
            (f" Q{st.session_state.filter_state['quarter'][1]}" 
             if st.session_state.filter_state['quarter'] != "All Quarters" else "")
        )
        st.markdown(f"<div style='text-align: right'>{status_text}</div>", unsafe_allow_html=True)
    
    # Determine filters based on selection
    if time_filter == "All Time":
        year_filters = None
        quarter_filters = None
    elif time_filter == "This Year":
        year_filters = [datetime.now().year]
        quarter_filters = None
    else:  # Custom
        year_filters = [st.session_state.filter_state['year']]
        quarter_filters = None if st.session_state.filter_state['quarter'] == "All Quarters" else [int(st.session_state.filter_state['quarter'][1])]
    
    # Check if filters changed
    current_filters = (year_filters, quarter_filters)
    if st.session_state.filter_state['current_filters'] != current_filters:
        st.session_state.payment_data = []
        st.session_state.payment_offset = 0
        st.session_state.filter_state['current_filters'] = current_filters
    
    # Load initial data if needed
    if len(st.session_state.payment_data) == 0:
        new_payments = get_paginated_payment_history(
            client_id,
            offset=0,
            limit=25,
            years=year_filters,
            quarters=quarter_filters
        )
        if new_payments:
            table_data = format_payment_data(new_payments)
            st.session_state.payment_data.extend(table_data)
    
    # Now check if we have any data to display
    if not st.session_state.payment_data:
        st.info("No payment history available for this client.", icon="ℹ️")
        return
    
    # Create DataFrame for display
    df = pd.DataFrame(st.session_state.payment_data)
    
    # Add CSS for payment rows
    st.markdown("""
        <style>
        /* Payment table specific styling */
        div.payment-table div[data-testid="column"] > div > div > div > div {
            padding: 0;
            margin: 0;
            line-height: 0.8;
        }
        
        /* Note button specific styling */
        div.payment-table div[data-testid="column"]:last-child button {
            padding: 0 !important;
            min-height: 24px !important;
            height: 24px !important;
            line-height: 24px !important;
            width: 24px !important;
            margin: 0 auto !important;
        }
        
        /* Payment table text */
        div.payment-table p {
            margin: 0;
            padding: 0;
            line-height: 1;
        }
        
        /* Header styling */
        div.payment-table div[data-testid="stHorizontalBlock"] {
            margin-bottom: 0.1rem;
        }
        
        /* Tooltip fix */
        div[data-testid="stTooltipIcon"] > div {
            min-height: auto !important;
            line-height: normal !important;
        }
        
        /* Note expansion area */
        div.payment-table div.stTextArea > div {
            margin: 0.25rem 0;
        }
        div.payment-table div.stTextArea textarea {
            min-height: 80px !important;
            padding: 0.5rem;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Wrap the payment table in a div with our specific class
    st.markdown('<div class="payment-table">', unsafe_allow_html=True)
    
    # Create scrollable container with optimized height
    st.markdown("""
        <style>
        div[data-testid="stVerticalBlock"] > div:has(div.stDataFrame) {
            height: 550px;  /* Slightly reduced height */
            overflow-y: auto;
            padding-right: 1rem;
            margin: 0.5rem 0;
        }
        div.stDataFrame {
            height: 100%;
            margin: 0;
        }
        div.stDataFrame thead th {
            position: sticky;
            top: 0;
            background: white;
            z-index: 1;
            padding: 0.15rem 0;
            line-height: 24px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Display headers with minimal spacing
    header_cols = st.columns([2, 2, 1, 2, 2, 2, 2, 2, 1])
    with header_cols[0]:
        st.markdown("<p style='font-weight: bold; margin: 0;'>Provider</p>", unsafe_allow_html=True)
    with header_cols[1]:
        st.markdown("<p style='font-weight: bold; margin: 0;'>Period</p>", unsafe_allow_html=True)
    with header_cols[2]:
        st.markdown("<p style='font-weight: bold; margin: 0;'>Frequency</p>", unsafe_allow_html=True)
    with header_cols[3]:
        st.markdown("<p style='font-weight: bold; margin: 0;'>Received</p>", unsafe_allow_html=True)
    with header_cols[4]:
        st.markdown("<p style='font-weight: bold; margin: 0;'>Total Assets</p>", unsafe_allow_html=True)
    with header_cols[5]:
        st.markdown("<p style='font-weight: bold; margin: 0;'>Expected Fee</p>", unsafe_allow_html=True)
    with header_cols[6]:
        st.markdown("<p style='font-weight: bold; margin: 0;'>Actual Fee</p>", unsafe_allow_html=True)
    with header_cols[7]:
        st.markdown("<p style='font-weight: bold; margin: 0;'>Discrepancy</p>", unsafe_allow_html=True)
    with header_cols[8]:
        st.markdown("<p style='font-weight: bold; margin: 0;'>Notes</p>", unsafe_allow_html=True)
    
    # Single header divider with minimal spacing
    st.markdown("<hr style='margin: 0.1rem 0; border-color: #eee;'>", unsafe_allow_html=True)
    
    # Display data rows
    for index, row in df.iterrows():
        # Create a container for the entire row including potential note
        with st.container():
            # Remove the hr lines between rows
            # if index > 0:
            #     st.markdown("<hr style='margin: 0.25rem 0; border-color: #eee;'>", unsafe_allow_html=True)
            
            # Create container for the row content
            with st.container():
                # First render the row with all columns
                row_cols = st.columns([2, 2, 1, 2, 2, 2, 2, 2, 1])
                
                with row_cols[0]:
                    st.markdown(f"<p style='margin: 0;'>{row['Provider']}</p>", unsafe_allow_html=True)
                with row_cols[1]:
                    st.markdown(f"<p style='margin: 0;'>{row['Period']}</p>", unsafe_allow_html=True)
                with row_cols[2]:
                    st.markdown(f"<p style='margin: 0;'>{row['Frequency']}</p>", unsafe_allow_html=True)
                with row_cols[3]:
                    st.markdown(f"<p style='margin: 0;'>{row['Received']}</p>", unsafe_allow_html=True)
                with row_cols[4]:
                    st.markdown(f"<p style='margin: 0;'>{row['Total Assets']}</p>", unsafe_allow_html=True)
                with row_cols[5]:
                    st.markdown(f"<p style='margin: 0;'>{row['Expected Fee']}</p>", unsafe_allow_html=True)
                with row_cols[6]:
                    st.markdown(f"<p style='margin: 0;'>{row['Actual Fee']}</p>", unsafe_allow_html=True)
                with row_cols[7]:
                    st.markdown(f"<p style='margin: 0;'>{row['Discrepancy']}</p>", unsafe_allow_html=True)
                with row_cols[8]:
                    has_note = bool(row["Notes"])
                    icon_content = "🟢" if has_note else "◯"
                    tooltip = row["Notes"] if has_note else "Add note"
                    
                    if st.button(
                        icon_content,
                        key=f"note_button_{row['payment_id']}",
                        help=tooltip,
                        use_container_width=False
                    ):
                        if 'active_note_id' in st.session_state and st.session_state.active_note_id == row['payment_id']:
                            st.session_state.active_note_id = None
                        else:
                            st.session_state.active_note_id = row['payment_id']
                        st.rerun()
            
            # After the row columns are closed, check if this row's note should be displayed
            if (
                'active_note_id' in st.session_state 
                and st.session_state.active_note_id == row['payment_id']
            ):
                # Create a fresh container for the note area
                with st.container():
                    # Create columns for the note area using full page width
                    note_cols = st.columns([7, 9])
                    with note_cols[1]:
                        st.markdown("""<div style="border-top: 1px solid #eee; padding-top: 0.25rem;"></div>""", unsafe_allow_html=True)
                        edited_note = st.text_area(
                            f"Note for {row['Provider']} - {row['Period']}",
                            value=row["Notes"] or "",
                            key=f"note_textarea_{row['payment_id']}",
                            height=80,
                            placeholder="Enter note here..."
                        )
                        
                        # Handle note changes
                        if edited_note != row["Notes"]:
                            update_payment_note(row['payment_id'], edited_note)
                            st.rerun()
    
    # Load more data if we're near the bottom
    if len(st.session_state.payment_data) < total_payments:
        if len(st.session_state.payment_data) % 25 == 0:  # Load next batch when we've displayed all current rows
            st.session_state.payment_offset = len(st.session_state.payment_data)
            new_payments = get_paginated_payment_history(
                client_id,
                offset=st.session_state.payment_offset,
                limit=25,  # Load 25 rows at a time
                years=year_filters,
                quarters=quarter_filters
            )
            if new_payments:
                table_data = format_payment_data(new_payments)
                st.session_state.payment_data.extend(table_data)
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_client_dashboard():
    """Display the client dashboard with proper state management."""
    st.write("👥 Client Dashboard")
    
    # Initialize all required states
    init_contact_form_state()
    init_payment_form_state()
    init_notes_state()
    init_filter_state()
    
    # Show contact form dialog if open
    if st.session_state.contact_form['is_open']:
        show_contact_form()
    
    # Reset state when changing clients
    if 'previous_client' not in st.session_state:
        st.session_state.previous_client = None
    
    # Client selector
    clients = get_clients()
    client_options = ["Select a client..."] + [client[1] for client in clients]
    selected_client_name = st.selectbox(
        "Client Selection",
        options=client_options,
        key="client_selector_dashboard",
        label_visibility="collapsed"
    )
    
    if selected_client_name != "Select a client...":
        # Clear all client-specific states when client changes
        if st.session_state.previous_client != selected_client_name:
            clear_client_specific_states()
            st.session_state.previous_client = selected_client_name
        
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
        
        show_payment_history(client_id)
    
# ============================================================================
# CONTACT CARD RENDERING
# ============================================================================

def render_contact_card(contact):
    """Render a single contact card with strict grid layout.
    
    Args:
        contact (tuple): Contact data tuple from database
            (contact_type, name, phone, email, fax, physical_address, mailing_address, contact_id)
    """
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
    