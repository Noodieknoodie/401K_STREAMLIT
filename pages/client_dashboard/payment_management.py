import streamlit as st
import pandas as pd
from datetime import datetime
from utils import (
    get_payment_history, update_payment_note,
    get_paginated_payment_history, get_total_payment_count,
    get_payment_year_quarters
)

@st.cache_data(ttl=300)  # Cache formatted data for 5 minutes
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
        
        # Format payment period with Q prefix
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

def render_note_cell(payment_id, note, provider, period):
    """Render a note cell with edit functionality."""
    # Initialize state for this note if not exists
    state_key = f"note_state_{payment_id}"
    if state_key not in st.session_state:
        st.session_state[state_key] = {
            "is_editing": False,
            "current_note": note,
            "has_changes": False
        }
    
    note_state = st.session_state[state_key]
    has_note = bool(note_state["current_note"])
    icon_content = "🟢" if has_note else "◯"
    
    # Create the note button with tooltip
    if st.button(
        icon_content, 
        key=f"note_button_{payment_id}",
        help=note_state["current_note"] if has_note else "Add note",
        use_container_width=False
    ):
        # Toggle editing state
        note_state["is_editing"] = not note_state["is_editing"]
    
    return note_state["is_editing"]  # Return if we should show the edit form

def initialize_filter_state():
    """Initialize or get filter state"""
    if 'filter_state' not in st.session_state:
        st.session_state.filter_state = {
            'time_filter': "All Time",
            'year': None,
            'quarter': None,
            'needs_reload': False
        }
    return st.session_state.filter_state

def handle_filter_change():
    """Mark that data needs to be reloaded due to filter change"""
    st.session_state.filter_state['needs_reload'] = True

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
    
    # Initialize filter state
    filter_state = initialize_filter_state()
    
    # Create a row with the same width as the table
    left_col, right_col = st.columns([6, 3])
    
    with left_col:
        time_filter = st.radio(
            "Time Filter",
            options=["All Time", "This Year", "Custom"],
            horizontal=True,
            label_visibility="collapsed",
            key="time_filter_radio",
            on_change=handle_filter_change
        )
        
        if time_filter == "Custom":
            col1, col2, _ = st.columns([1, 1, 2])
            with col1:
                year = st.selectbox(
                    "Select Year",
                    options=years,
                    index=0,
                    label_visibility="collapsed",
                    key="year_select",
                    on_change=handle_filter_change
                )
            with col2:
                quarter = st.selectbox(
                    "Select Quarter",
                    options=["All Quarters", "Q1", "Q2", "Q3", "Q4"],
                    index=0,
                    label_visibility="collapsed",
                    key="quarter_select",
                    on_change=handle_filter_change
                )
    
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
    
    with right_col:
        status_text = (
            f"Viewing all {total_payments} payments" if time_filter == "All Time" else
            f"Viewing payments from {datetime.now().year}" if time_filter == "This Year" else
            f"Viewing payments from {year}" + (f" Q{quarter[1]}" if quarter != "All Quarters" else "")
        )
        st.markdown(f"<div style='text-align: right'>{status_text}</div>", unsafe_allow_html=True)
    
    # Check if filters actually changed
    current_filters = (year_filters, quarter_filters)
    if filter_state['needs_reload'] or (
        'current_filters' not in st.session_state or 
        st.session_state.current_filters != current_filters
    ):
        st.session_state.payment_data = []
        st.session_state.payment_offset = 0
        st.session_state.current_filters = current_filters
        filter_state['needs_reload'] = False
        
        # Only clear note states if filters actually changed
        for key in list(st.session_state.keys()):
            if key.startswith('note_state_'):
                del st.session_state[key]
    
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
    for index, row in df.iterrows():
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
            is_editing = render_note_cell(row["payment_id"], row["Notes"], row["Provider"], row["Period"])
        
        # Note editing form - now properly spans the full width
        if is_editing:
            st.markdown(f"""<div style="border-top: 1px solid #eee; padding-top: 0.5rem;"></div>""", unsafe_allow_html=True)
            note_cols = st.columns([7, 9])  # Same ratio as original
            with note_cols[1]:
                state_key = f"note_state_{row['payment_id']}"
                new_note = st.text_area(
                    f"Note for {row['Provider']} - {row['Period']}",
                    value=st.session_state[state_key]["current_note"] or "",
                    key=f"note_textarea_{row['payment_id']}",
                    height=100,
                    placeholder="Enter note here..."
                )
                
                # Only update if note content changed
                if new_note != st.session_state[state_key]["current_note"]:
                    update_payment_note(row["payment_id"], new_note)
                    st.session_state[state_key]["current_note"] = new_note
                    st.session_state[state_key]["has_changes"] = True
    
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
    