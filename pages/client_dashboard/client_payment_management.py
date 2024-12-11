import streamlit as st
import pandas as pd
from datetime import datetime
from utils.utils import (
    get_payment_history, update_payment_note,
    get_clients, get_contacts,
    get_client_details, add_contact, update_contact,
    delete_contact, get_payment_year_quarters, get_payment_by_id, format_currency_ui,
    get_client_dashboard_data,
)

from utils.perf_logging import log_event
from .client_payment_form import (
    show_payment_form,
    populate_payment_form_for_edit,
    init_payment_form
)

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
    elif not st.session_state.contact_form.get('explicit_open', False):
        # If form wasn't explicitly opened by a button click, ensure it stays closed
        st.session_state.contact_form['is_open'] = False
    
    if 'delete_contact_id' not in st.session_state:
        st.session_state.delete_contact_id = None
    if 'show_delete_confirm' not in st.session_state:
        st.session_state.show_delete_confirm = False

def open_contact_form(contact_type=None, mode='add', contact_data=None):
    """Explicitly open the contact form with the given parameters."""
    if 'contact_form' not in st.session_state:
        init_contact_form_state()
    
    st.session_state.contact_form.update({
        'is_open': True,
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
            'is_open': False,
            'explicit_open': False,
            'mode': 'add',
            'contact_type': None,
            'contact_id': None,
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
        })

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

# ============================================================================
# FILTER STATE MANAGEMENT
# ============================================================================

def init_filter_state():
    """Initialize payment history filter state"""
    if 'filter_state' not in st.session_state:
        st.session_state.filter_state = {
            'time_filter': 'All Time',  # 'All Time', 'This Year', 'Custom'
            'year': datetime.now().year,
            'quarter': None,
            'current_filters': None  # Keep for backward compatibility
        }

def update_filter_state(key, value):
    """Update filter state and handle dependencies"""
    if key == 'time_filter':
        st.session_state.filter_state['time_filter'] = value
        if value == 'All Time':
            st.session_state.filter_state['year'] = None
            st.session_state.filter_state['quarter'] = None
        elif value == 'This Year':
            st.session_state.filter_state['year'] = datetime.now().year
            st.session_state.filter_state['quarter'] = None
    else:
        st.session_state.filter_state[key] = value

def get_current_filters():
    """Get current year and quarter filters based on filter state"""
    filter_state = st.session_state.filter_state
    time_filter = filter_state['time_filter']
    
    if time_filter == 'All Time':
        return None, None
    elif time_filter == 'This Year':
        return [datetime.now().year], None
    else:  # Custom
        year = filter_state['year']
        quarter = filter_state['quarter']
        return (
            [year] if year else None,
            [int(quarter[1])] if quarter and quarter != "All Quarters" else None
        )

def clear_client_specific_states():
    """Clear all client-specific states when switching clients."""
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
    
    # Reset payment form
    if 'payment_form' in st.session_state:
        st.session_state.payment_form['is_visible'] = False
        st.session_state.payment_form['client_id'] = None
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

# DO NOT REMOVE NOTE FUNCTIONALITY KEEP NOTES EXACTLY AS THEY ARE             

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
    init_payment_form()
    init_notes_state()
    init_filter_state()
    
    # Initialize delete confirmation state
    if 'delete_payment_id' not in st.session_state:
        st.session_state.delete_payment_id = None
    if 'show_delete_confirm' not in st.session_state:
        st.session_state.show_delete_confirm = False
    
    # Get data first
    year_quarters = get_payment_year_quarters(client_id)
    
    # Get available years
    years = sorted(list(set(yq[0] for yq in year_quarters)), reverse=True)
    if not years:
        st.info("No payment history available.")
        return
    
    # Create a row with the same width as the table
    left_col, middle_col, right_col = st.columns([4, 2, 4])
    
    with left_col:
        st.radio(
            "Time Period Filter",
            options=["All Time", "This Year", "Custom"],
            key="filter_time_period",
            horizontal=True,
            label_visibility="collapsed",
            on_change=lambda: update_filter_state('time_filter', st.session_state.filter_time_period)
        )
        
        if st.session_state.filter_state['time_filter'] == "Custom":
            col1, col2, _ = st.columns([1, 1, 2])
            with col1:
                st.selectbox(
                    "Select Year",
                    options=years,
                    index=years.index(st.session_state.filter_state['year']) if st.session_state.filter_state['year'] in years else 0,
                    key="filter_year",
                    label_visibility="collapsed",
                    on_change=lambda: update_filter_state('year', st.session_state.filter_year)
                )
            with col2:
                st.selectbox(
                    "Select Quarter",
                    options=["All Quarters", "Q1", "Q2", "Q3", "Q4"],
                    index=0,
                    key="filter_quarter",
                    label_visibility="collapsed",
                    on_change=lambda: update_filter_state('quarter', st.session_state.filter_quarter)
                )
    
    with middle_col:
        if st.button("Add Payment", type="primary", use_container_width=True):
            st.session_state.payment_form['is_visible'] = True
            st.rerun()
    
    with right_col:
        filter_state = st.session_state.filter_state
        status_text = (
            f"Showing all payments" if filter_state['time_filter'] == "All Time" else
            f"Showing payments from {datetime.now().year}" if filter_state['time_filter'] == "This Year" else
            f"Showing payments from {filter_state['year']}" + 
            (f" Q{filter_state['quarter'][1]}" 
             if filter_state['quarter'] and filter_state['quarter'] != "All Quarters" else "")
        )
        st.markdown(f"<div style='text-align: right'>{status_text}</div>", unsafe_allow_html=True)
    
    # Get filtered data using the helper function
    year_filters, quarter_filters = get_current_filters()
    
    # Load and format all payment data
    payments = get_payment_history(client_id, years=year_filters, quarters=quarter_filters)
    if not payments:
        st.info("No payment history available for this client.", icon="ℹ️")
        return
    
    table_data = format_payment_data(payments)
    df = pd.DataFrame(table_data)
    
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
        
        /* Action buttons styling */
        div.payment-table div[data-testid="column"]:nth-last-child(1) button {
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
    
    # Display headers with minimal spacing
    header_cols = st.columns([2, 2, 1, 2, 2, 2, 2, 2, 1, 1])
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
    with header_cols[9]:
        st.markdown("<p style='font-weight: bold; margin: 0;'>Actions</p>", unsafe_allow_html=True)
    
    # Single header divider with minimal spacing
    st.markdown("<hr style='margin: 0.1rem 0; border-color: #eee;'>", unsafe_allow_html=True)

# DO NOT REMOVE NOTE FUNCTIONALITY KEEP NOTES EXACTLY AS THEY ARE        

    # Display data rows
    for index, row in df.iterrows():
        render_table_row(row)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_table_row(row):
    """Render a single payment table row"""
    with st.container():
        row_cols = st.columns([2, 2, 1, 2, 2, 2, 2, 2, 1, 1])
        
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
                # Save any existing active note before switching
                if ('active_note_id' in st.session_state and 
                    st.session_state.active_note_id != row['payment_id'] and
                    'note_textarea_' + str(st.session_state.active_note_id) in st.session_state):
                    prev_note = st.session_state['note_textarea_' + str(st.session_state.active_note_id)]
                    update_payment_note(st.session_state.active_note_id, prev_note)
                
                # Toggle note state
                if 'active_note_id' in st.session_state and st.session_state.active_note_id == row['payment_id']:
                    st.session_state.active_note_id = None
                else:
                    st.session_state.active_note_id = row['payment_id']
                    # Ensure contact form stays closed
                    if 'contact_form' in st.session_state:
                        st.session_state.contact_form['is_open'] = False
                
                st.rerun()
        
        with row_cols[9]:
            action_cols = st.columns([1, 1])
            with action_cols[0]:
                if st.button("✏️", key=f"editpayment{row['payment_id']}", help="Edit payment"):
                    payment_data = get_payment_by_id(row['payment_id'])
                    if payment_data:
                        st.session_state.payment_form['is_visible'] = True
                        st.session_state.payment_form['mode'] = 'edit'
                        st.session_state.payment_form['payment_id'] = row['payment_id']
                        populate_payment_form_for_edit(payment_data)
                    st.rerun()
            with action_cols[1]:
                if st.button("🗑️", key=f"deletepayment{row['payment_id']}", help="Delete payment"):
                    st.session_state.delete_payment_id = row['payment_id']
                    st.session_state.show_delete_confirm = True
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

def display_client_dashboard():
    """Display the main client dashboard with optimized data loading"""
    # Initialize states
    init_contact_form_state()
    init_payment_form()
    init_notes_state()
    init_filter_state()
    
    # Get selected client
    if 'client_selector_dashboard' not in st.session_state:
        st.warning("Please select a client from the sidebar.")
        return
        
    client_name = st.session_state.client_selector_dashboard
    client_id = next(
        client[0] for client in get_clients()
        if client[1] == client_name
    )
    
    # Load all client data efficiently
    if ('client_data' not in st.session_state or 
        st.session_state.get('current_client_id') != client_id):
        st.session_state.client_data = load_client_data(client_id)
        st.session_state.current_client_id = client_id
    
    # Display client sections
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Payment History")
        display_payments_section()
    
    with col2:
        st.subheader("Contacts")
        display_contacts_section()
        
        # Add Contact button
        contact_types = ["Primary Contact", "Authorized Contact", "Provider Contact"]
        for contact_type in contact_types:
            if st.button(f"Add {contact_type}", key=f"add_{contact_type.lower().replace(' ', '_')}"):
                open_contact_form(contact_type=contact_type)
                st.rerun()
    
    # Show forms if needed - only show one at a time
    if st.session_state.payment_form['is_visible']:
        show_payment_form()
    elif st.session_state.contact_form['is_open']:
        show_contact_form()

def display_payments_section():
    """Display the payments section using the new data structure"""
    if 'client_data' not in st.session_state:
        return
        
    payments_data = st.session_state.client_data['recent_payments']
    if not payments_data:
        st.info("No payment history found for this client.")
        return
    
    # Create DataFrame from payments data
    df = pd.DataFrame(payments_data)
    
    # Add payment form button
    if st.button("Add Payment", type="primary"):
        st.session_state.payment_form['is_visible'] = True
        st.rerun()
    
    # Display payments in a table format
    for payment in payments_data:
        with st.container():
            row_cols = st.columns([2, 1, 1, 1, 1, 1, 2, 1, 1, 1])
            
            # Provider
            with row_cols[0]:
                st.write(payment['provider_name'])
            
            # Period
            with row_cols[1]:
                period = f"Q{payment['applied_start_quarter']} {payment['applied_start_year']}"
                if payment['applied_end_quarter']:
                    period += f" - Q{payment['applied_end_quarter']} {payment['applied_end_year']}"
                st.write(period)
            
            # Schedule
            with row_cols[2]:
                st.write(payment['payment_schedule'])
            
            # Received Date
            with row_cols[3]:
                st.write(payment['received_date'])
            
            # Total Assets
            with row_cols[4]:
                st.write(format_currency_ui(payment['total_assets']))
            
            # Expected Fee
            with row_cols[5]:
                st.write(format_currency_ui(payment['expected_fee']))
            
            # Actual Fee
            with row_cols[6]:
                st.write(format_currency_ui(payment['actual_fee']))
            
            # Notes
            with row_cols[7]:
                tooltip = payment['notes'] if payment['notes'] else "Click to add notes"
                if st.button(
                    "📝",
                    key=f"notes{payment['payment_id']}",
                    help=tooltip,
                    use_container_width=False
                ):
                    if 'active_note_id' in st.session_state and st.session_state.active_note_id == payment['payment_id']:
                        st.session_state.active_note_id = None
                    else:
                        st.session_state.active_note_id = payment['payment_id']
                    st.rerun()
            
            # Edit/Delete buttons
            with row_cols[8]:
                action_cols = st.columns([1, 1])
                with action_cols[0]:
                    if st.button("✏️", key=f"editpayment{payment['payment_id']}", help="Edit payment"):
                        payment_data = get_payment_by_id(payment['payment_id'])
                        if payment_data:
                            st.session_state.payment_form['is_visible'] = True
                            st.session_state.payment_form['mode'] = 'edit'
                            st.session_state.payment_form['payment_id'] = payment['payment_id']
                            populate_payment_form_for_edit(payment_data)
                        st.rerun()
                with action_cols[1]:
                    if st.button("🗑️", key=f"deletepayment{payment['payment_id']}", help="Delete payment"):
                        st.session_state.delete_payment_id = payment['payment_id']
                        st.session_state.show_delete_confirm = True
                        st.rerun()
            
            # Show delete confirmation if needed
            if (
                st.session_state.show_delete_confirm 
                and st.session_state.delete_payment_id == payment['payment_id']
            ):
                with st.container():
                    confirm_cols = st.columns([7, 3])
                    with confirm_cols[1]:
                        st.warning("Delete this payment?")
                        if st.button("Yes", key=f"confirm_delete_{payment['payment_id']}", type="primary"):
                            # Add delete payment logic here
                            st.session_state.show_delete_confirm = False
                            st.rerun()
                        if st.button("No", key=f"cancel_delete_{payment['payment_id']}"):
                            st.session_state.show_delete_confirm = False
                            st.rerun()

# ============================================================================
# DATA LOADING
# ============================================================================

def load_client_data(client_id):
    """Load all client data efficiently using a single database call"""
    data = get_client_dashboard_data(client_id)
    st.session_state.client_data = data
    return data

# ============================================================================
# CONTACT DISPLAY
# ============================================================================

def render_contact_card(contact_data):
    """Render a contact card with the given contact data from JSON"""
    with st.container():
        info_col, action_col = st.columns([6, 1])
        
        with info_col:
            st.markdown(f"##### {contact_data['contact_name']} ({contact_data['contact_type']})")
            
            col1, col2 = st.columns(2)
            with col1:
                if contact_data['phone']:
                    st.write("📞 " + contact_data['phone'])
                if contact_data['email']:
                    st.write("📧 " + contact_data['email'])
                if contact_data['fax']:
                    st.write("📠 " + contact_data['fax'])
            
            with col2:
                if contact_data['physical_address']:
                    st.write("🏢 " + contact_data['physical_address'])
                if contact_data['mailing_address']:
                    st.write("📫 " + contact_data['mailing_address'])
        
        with action_col:
            if st.button("✏️", key=f"edit_{contact_data['contact_id']}", help="Edit contact"):
                st.session_state.contact_form['mode'] = 'edit'
                st.session_state.contact_form['is_open'] = True
                st.session_state.contact_form['contact_type'] = contact_data['contact_type']
                st.session_state.contact_form['contact_id'] = contact_data['contact_id']
                st.session_state.contact_form['form_data'] = {
                    'contact_name': contact_data['contact_name'] or '',
                    'phone': contact_data['phone'] or '',
                    'email': contact_data['email'] or '',
                    'fax': contact_data['fax'] or '',
                    'physical_address': contact_data['physical_address'] or '',
                    'mailing_address': contact_data['mailing_address'] or ''
                }
                st.rerun()
            if st.button("🗑️", key=f"delete_{contact_data['contact_id']}", help="Delete contact"):
                st.session_state.delete_contact_id = contact_data['contact_id']
                st.session_state.show_delete_confirm = True
                st.rerun()
        
        st.divider()

def display_contacts_section():
    """Display the contacts section using the new data structure"""
    if 'client_data' not in st.session_state:
        return
    
    contacts_data = st.session_state.client_data['contacts']
    if not contacts_data:
        st.info("No contacts found for this client.")
        return
        
    # Sort contacts by type
    contact_type_order = {'Primary': 1, 'Authorized': 2, 'Provider': 3}
    sorted_contacts = sorted(
        contacts_data,
        key=lambda x: (contact_type_order.get(x['contact_type'], 4), x['contact_name'])
    )
    
    for contact in sorted_contacts:
        render_contact_card(contact)

if __name__ == "__main__":
    display_client_dashboard()
    