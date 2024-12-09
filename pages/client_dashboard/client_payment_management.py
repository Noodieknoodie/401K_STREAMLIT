import streamlit as st
import pandas as pd
from datetime import datetime
from utils.utils import (
    get_payment_history, update_payment_note,
    get_paginated_payment_history, get_total_payment_count,
    get_payment_year_quarters
)

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
    update_payment_note(payment_id, new_note)
    if 'notes_state' in st.session_state:
        st.session_state.notes_state['active_note'] = None
    st.rerun()

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
    has_note, icon_content, tooltip = format_note_display(note)
    
    # Create the note button with tooltip
    if st.button(
        icon_content, 
        key=f"note_button_{payment_id}",
        help=tooltip,
        use_container_width=False
    ):
        notes_state = st.session_state.notes_state
        
        # Auto-save previous note if exists
        if notes_state['active_note'] and notes_state['active_note'] != payment_id:
            prev_id = notes_state['active_note']
            if prev_id in notes_state['edited_notes']:
                handle_note_edit(prev_id, notes_state['edited_notes'][prev_id])
                notes_state['edited_notes'].pop(prev_id)
        
        # Toggle note state
        if notes_state['active_note'] == payment_id:
            if payment_id in notes_state['edited_notes']:
                handle_note_edit(payment_id, notes_state['edited_notes'][payment_id])
                notes_state['edited_notes'].pop(payment_id)
            notes_state['active_note'] = None
        else:
            notes_state['active_note'] = payment_id
        
        st.rerun()
    
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

def show_payment_history(client_id):
    """Display payment history with efficient layout and smart navigation."""
    
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
            "",
            options=["All Time", "This Year", "Custom"],
            horizontal=True,
            label_visibility="collapsed"
        )
        
        if time_filter == "Custom":
            col1, col2, _ = st.columns([1, 1, 2])
            with col1:
                year = st.selectbox("Year", options=years, index=0, label_visibility="collapsed")
            with col2:
                quarter = st.selectbox(
                    "Quarter",
                    options=["All Quarters", "Q1", "Q2", "Q3", "Q4"],
                    index=0,
                    label_visibility="collapsed"
                )
    
    with middle_col:
        if st.button("Add Payment", type="primary", use_container_width=True):
            st.session_state.payment_form['is_open'] = True
            st.rerun()
    
    with right_col:
        status_text = (
            f"Viewing all {total_payments} payments" if time_filter == "All Time" else
            f"Viewing payments from {datetime.now().year}" if time_filter == "This Year" else
            f"Viewing payments from {year}" + (f" Q{quarter[1]}" if quarter != "All Quarters" else "")
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
        year_filters = [year]
        quarter_filters = None if quarter == "All Quarters" else [int(quarter[1])]
    
    # Check if filters changed
    current_filters = (year_filters, quarter_filters)
    if ('current_filters' not in st.session_state or 
        st.session_state.current_filters != current_filters):
        st.session_state.payment_data = []
        st.session_state.payment_offset = 0
        st.session_state.current_filters = current_filters
    
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
    
    # Create scrollable container with fixed height
    st.markdown("""
        <style>
        div[data-testid="stVerticalBlock"] > div:has(div.stDataFrame) {
            height: 600px;
            overflow-y: auto;
            padding-right: 1rem;
        }
        div.stDataFrame {
            height: 100%;
        }
        div.stDataFrame thead th {
            position: sticky;
            top: 0;
            background: white;
            z-index: 1;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Display rows
    # Add headers first
    header_cols = st.columns([2, 2, 1, 2, 2, 2, 2, 2, 1])
    with header_cols[0]:
        st.markdown("**Provider**")
    with header_cols[1]:
        st.markdown("**Period**")
    with header_cols[2]:
        st.markdown("**Frequency**")
    with header_cols[3]:
        st.markdown("**Received**")
    with header_cols[4]:
        st.markdown("**Total Assets**")
    with header_cols[5]:
        st.markdown("**Expected Fee**")
    with header_cols[6]:
        st.markdown("**Actual Fee**")
    with header_cols[7]:
        st.markdown("**Discrepancy**")
    with header_cols[8]:
        st.markdown("**Notes**")
    
    st.markdown("<hr style='margin: 0.5rem 0; border-color: #eee;'>", unsafe_allow_html=True)
    
    # Display data rows
    for index, row in df.iterrows():
        # First render the row with all columns
        row_cols = st.columns([2, 2, 1, 2, 2, 2, 2, 2, 1])
        
        with row_cols[0]:
            st.write(row["Provider"])
        with row_cols[1]:
            st.write(row["Period"])
        with row_cols[2]:
            st.write(row["Frequency"])
        with row_cols[3]:
            st.write(row["Received"])
        with row_cols[4]:
            st.write(row["Total Assets"])
        with row_cols[5]:
            st.write(row["Expected Fee"])
        with row_cols[6]:
            st.write(row["Actual Fee"])
        with row_cols[7]:
            st.write(row["Discrepancy"])
        with row_cols[8]:
            # Just render the note button here
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
            # Create a fresh container outside the row structure
            with st.container():
                # Create columns for the note area using full page width
                note_cols = st.columns([7, 9])
                with note_cols[1]:
                    st.markdown("""<div style="border-top: 1px solid #eee; padding-top: 0.5rem;"></div>""", unsafe_allow_html=True)
                    edited_note = st.text_area(
                        f"Note for {row['Provider']} - {row['Period']}",
                        value=row["Notes"] or "",
                        key=f"note_textarea_{row['payment_id']}",
                        height=100,
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
    