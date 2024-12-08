import streamlit as st
import pandas as pd
from datetime import datetime
from utils.utils import (
    get_payment_history, get_paginated_payment_history,
    get_total_payment_count, get_payment_year_quarters,
    format_payment_data, update_payment_note, get_clients
)
from .payment_form import show_payment_form, init_payment_form_state

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
    
    # Show note editing form if active
    if (
        'active_note_payment_id' in st.session_state 
        and st.session_state.active_note_payment_id == payment_id
    ):
        with st.container():
            note_cols = st.columns([7, 9])
            with note_cols[1]:
                st.markdown("""<div style="border-top: 1px solid #eee; padding-top: 0.5rem;"></div>""", unsafe_allow_html=True)
                st.text_area(
                    f"Note",
                    value=note or "",
                    key=f"note_textarea_{payment_id}",
                    height=100,
                    placeholder="Enter note here..."
                )

def show_quarterly_summary():
    """Display the quarterly summary page with payment history"""
    st.title("📊 Quarterly Summary")
    
    # Initialize payment form state
    init_payment_form_state()
    
    # Get client selection
    clients = get_clients()  # Make sure this is imported from utils
    if not clients:
        st.warning("No clients found in the system.")
        return
        
    selected_client = st.selectbox(
        "Select Client",
        options=clients,
        format_func=lambda x: x[1],  # Display the client name
        key="selected_client"
    )
    
    client_id = selected_client[0] if selected_client else None
    
    # Show payment form dialog if open
    if 'payment_form' in st.session_state and st.session_state.payment_form['is_open']:
        show_payment_form(client_id)
    
    # Get data first
    total_payments = get_total_payment_count(client_id)
    year_quarters = get_payment_year_quarters(client_id)
    
    # Get available years
    years = sorted(list(set(yq[0] for yq in year_quarters)), reverse=True)
    if not years:
        st.info("No payment history available for this client.")
        return
    
    # Create a row with three columns for filters and actions
    col1, col2, col3 = st.columns([4, 4, 4])
    
    with col1:
        time_filter = st.radio(
            "Time Period",  # Added label here
            options=["All Time", "This Year", "Custom"],
            horizontal=True,
            label_visibility="collapsed"
        )
        
        if time_filter == "Custom":
            year_col, quarter_col, _ = st.columns([1, 1, 2])
            with year_col:
                year = st.selectbox("Select Year", options=years, index=0)  # Added proper label
            with quarter_col:
                quarter = st.selectbox(
                    "Select Quarter",  # Added proper label
                    options=["All Quarters", "Q1", "Q2", "Q3", "Q4"],
                    index=0
                )
    
    with col2:
        if client_id:  # Only show Add Payment button if a client is selected
            if st.button("Add Payment", type="primary"):
                st.session_state.payment_form['is_open'] = True
                st.rerun()
        else:
            st.info("Please select a client to add payments")
    
    with col3:
        status_text = (
            f"Viewing all {total_payments} payments" if time_filter == "All Time" else
            f"Viewing payments from {datetime.now().year}" if time_filter == "This Year" else
            f"Viewing payments from {year}" + (f" Q{quarter[1]}" if quarter != "All Quarters" else "")
        )
        st.markdown(f"<div style='text-align: right'>{status_text}</div>", unsafe_allow_html=True)
    
    # Add table headers
    cols = st.columns([2, 2, 1, 2, 2, 2, 2, 2, 1, 1])
    headers = ["Provider", "Period", "Frequency", "Received", "Total Assets", 
              "Expected Fee", "Actual Fee", "Discrepancy", "Method", "Notes"]
    
    # Style for headers
    header_style = """
        <style>
            .header-text {
                font-weight: bold;
                color: #262730;
                font-size: 0.9rem;
                font-family: "Source Sans Pro", sans-serif;
                margin-bottom: 0.5rem;
            }
            .payment-row:hover {
                background-color: #f8f9fa;
            }
            .payment-cell {
                padding: 0.5rem 0;
            }
        </style>
    """
    st.markdown(header_style, unsafe_allow_html=True)
    
    # Display headers
    for col, header in zip(cols, headers):
        with col:
            st.markdown(f"<div class='header-text'>{header}</div>", unsafe_allow_html=True)
    
    # Add a subtle separator
    st.markdown("<hr style='margin: 0; padding: 0; background-color: #f0f0f0;'>", unsafe_allow_html=True)
    
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
            client_id,  # None for all clients
            offset=0,
            limit=25,
            years=year_filters,
            quarters=quarter_filters
        )
        if new_payments:
            table_data = format_payment_data(new_payments)
            st.session_state.payment_data.extend(table_data)
    
    # Display payment data
    if not st.session_state.payment_data:
        st.info("No payments found for the selected filters.")
        return
    
    # Create DataFrame for display
    df = pd.DataFrame(st.session_state.payment_data)
    
    # Display rows
    for index, row in df.iterrows():
        st.markdown("""<div class="payment-row">""", unsafe_allow_html=True)
        cols = st.columns([2, 2, 1, 2, 2, 2, 2, 2, 1, 1])
        
        with cols[0]:
            st.markdown(f"""<div class="payment-cell">{row["Provider"]}</div>""", unsafe_allow_html=True)
        with cols[1]:
            st.markdown(f"""<div class="payment-cell">{row["Period"]}</div>""", unsafe_allow_html=True)
        with cols[2]:
            st.markdown(f"""<div class="payment-cell">{row["Frequency"]}</div>""", unsafe_allow_html=True)
        with cols[3]:
            st.markdown(f"""<div class="payment-cell">{row["Received"]}</div>""", unsafe_allow_html=True)
        with cols[4]:
            st.markdown(f"""<div class="payment-cell">{row["Total Assets"]}</div>""", unsafe_allow_html=True)
        with cols[5]:
            st.markdown(f"""<div class="payment-cell">{row["Expected Fee"]}</div>""", unsafe_allow_html=True)
        with cols[6]:
            st.markdown(f"""<div class="payment-cell">{row["Actual Fee"]}</div>""", unsafe_allow_html=True)
        with cols[7]:
            st.markdown(f"""<div class="payment-cell">{row["Discrepancy"]}</div>""", unsafe_allow_html=True)
        with cols[8]:
            st.markdown(f"""<div class="payment-cell">{row["Method"]}</div>""", unsafe_allow_html=True)
        with cols[9]:
            render_note_cell(row["payment_id"], row["Notes"])
        
        st.markdown("""</div>""", unsafe_allow_html=True)
        
        # Note editing form
        if (
            'active_note_payment_id' in st.session_state 
            and st.session_state.active_note_payment_id == row["payment_id"]
        ):
            with st.container():
                note_cols = st.columns([7, 9])
                with note_cols[1]:
                    st.markdown("""<div style="border-top: 1px solid #eee; padding-top: 0.5rem;"></div>""", unsafe_allow_html=True)
                    st.text_area(
                        f"Note for {row['Provider']} - {row['Period']}",
                        value=row["Notes"] or "",
                        key=f"note_textarea_{row['payment_id']}",
                        height=100,
                        placeholder="Enter note here..."
                    )