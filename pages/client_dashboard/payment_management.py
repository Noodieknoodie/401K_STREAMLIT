import streamlit as st
import pandas as pd
from datetime import datetime
from utils.utils import (
    get_payment_history, update_payment_note, get_viewport_record_count,
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

def handle_note_edit(payment_id, new_note):
    """Handle updating a payment note."""
    update_payment_note(payment_id, new_note)
    if 'active_note_payment_id' in st.session_state:
        del st.session_state.active_note_payment_id
    st.rerun()

def render_note_cell(payment_id, note):
    """Render a note cell with edit functionality."""
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
    left_col, right_col = st.columns([6, 3])
    
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
    
    with right_col:
        status_text = (
            f"Viewing all {total_payments} payments" if time_filter == "All Time" else
            f"Viewing payments from {datetime.now().year}" if time_filter == "This Year" else
            f"Viewing payments from {year}" + (f" Q{quarter[1]}" if quarter != "All Quarters" else "")
        )
        st.markdown(f"<div style='text-align: right'>*{status_text}*</div>", unsafe_allow_html=True)
    
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
    
    # Get viewport size and records per page
    records_per_page = get_viewport_record_count()
    
    # Load more data if needed
    if (not st.session_state.payment_data or 
        st.session_state.payment_offset >= len(st.session_state.payment_data)):
        new_payments = get_paginated_payment_history(
            client_id,
            offset=st.session_state.payment_offset,
            limit=records_per_page,
            years=year_filters,
            quarters=quarter_filters
        )
        
        if new_payments:
            table_data = format_payment_data(new_payments)
            st.session_state.payment_data.extend(table_data)
    
    if not st.session_state.payment_data:
        st.info("No payment history available for this client.", icon="ℹ️")
        return
    
    # Create DataFrame for display
    df = pd.DataFrame(st.session_state.payment_data)
    
    # Scrollable container for the table
    st.markdown('<div class="payment-container">', unsafe_allow_html=True)
    
    # Display headers (sticky)
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
    
    # Display rows
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
            
            # Note editing form
            if (
                'active_note_payment_id' in st.session_state 
                and st.session_state.active_note_payment_id == row["payment_id"]
            ):
                with st.container():
                    note_cols = st.columns([7, 9])
                    with note_cols[1]:
                        st.markdown(f"""<div style="border-top: 1px solid #eee; padding-top: 0.5rem;"></div>""", unsafe_allow_html=True)
                        st.text_area(
                            f"Note for {row['Provider']} - {row['Period']}",
                            value=row["Notes"] or "",
                            key=f"note_textarea_{row['payment_id']}",
                            height=100,
                            placeholder="Enter note here..."
                        )
    
    st.markdown('</div>', unsafe_allow_html=True)  # End of scrollable container
    
    # Navigation controls
    if len(st.session_state.payment_data) > get_viewport_record_count():
        st.markdown(
            f"""
            <div class="scroll-top">
                <button kind="secondary" class="stButton">
                    <div style="font-size: 24px;">⬆️</div>
                </button>
            </div>
            <script>
                const btn = document.querySelector('.scroll-top button');
                btn.onclick = () => {{
                    document.querySelector('.payment-container').scrollTo({{
                        top: 0,
                        behavior: 'smooth'
                    }});
                }};
            </script>
            """,
            unsafe_allow_html=True
        )
    
    # Load more button at bottom
    if len(st.session_state.payment_data) < total_payments:
        st.markdown('<div class="load-more">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("Load More", use_container_width=True):
                st.session_state.payment_offset = len(st.session_state.payment_data)
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True) 