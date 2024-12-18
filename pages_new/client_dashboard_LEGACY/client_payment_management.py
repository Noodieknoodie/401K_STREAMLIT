# pages\client_dashboard\client_payment_management.py
import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from utils.utils import (
    get_payment_history,
    update_payment_note,
    get_payment_year_quarters,
    get_payment_by_id,
    format_currency_ui,
    delete_payment
)
from utils.ui_state_manager import UIStateManager
from .client_payment_form import show_payment_dialog

# ============================================================================
# STATE MANAGEMENT
# ============================================================================

def init_filter_state():
    """Initialize payment history filter state"""
    if 'filter_state' not in st.session_state:
        initial_state = {
            'time_filter': 'All Time',  # 'All Time', 'This Year', 'Custom'
            'year': datetime.now().year,
            'quarter': None,
            'current_filters': None
        }
        st.session_state.filter_state = initial_state

def update_filter_state(key: str, value: Any) -> None:
    """Update filter state and handle dependencies"""
    old_state = st.session_state.filter_state.copy()
    
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
        result = (None, None)
    elif time_filter == 'This Year':
        result = ([datetime.now().year], None)
    else:  # Custom
        year = filter_state['year']
        quarter = filter_state['quarter']
        result = (
            [year] if year else None,
            [int(quarter[1])] if quarter and quarter != "All Quarters" else None
        )
    return result

def init_notes_state():
    """Initialize centralized notes state management"""
    if 'notes_state' not in st.session_state:
        initial_state = {
            'active_note': None,
            'edited_notes': {},
            'temp_notes': {}
        }
        st.session_state.notes_state = initial_state

# ============================================================================
# DATA FORMATTING AND DISPLAY
# ============================================================================

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
        method = payment[12] or "N/A"
        
        formatted_payment = {
            "Provider": provider_name,
            "Period": period,
            "Frequency": frequency,
            "Method": method,
            "Received": received_date,
            "Total Assets": total_assets,
            "Expected Fee": expected_fee,
            "Actual Fee": actual_fee,
            "Discrepancy": discrepancy_str,
            "Notes": notes,
            "payment_id": payment_id
        }
        
        table_data.append(formatted_payment)
    
    return table_data

# ============================================================================
# NOTE HANDLING
# ============================================================================

def format_note_display(note):
    """Format note for display with caching."""
    formatted = (bool(note), "🟢" if note else "◯", note if note else "Add note")
    return formatted

def initialize_notes_state():
    """Initialize centralized note state management."""
    if 'notes_state' not in st.session_state:
        initial_state = {
            'active_note': None,
            'edited_notes': {}
        }
        st.session_state.notes_state = initial_state

def render_note_cell(payment_id, note, provider=None, period=None, ui_manager=None):
    """Render a note cell with edit functionality using centralized state."""
    initialize_notes_state()
    
    # Get cached note display format
    has_note = bool(note)
    icon_content = "🟢" if has_note else "◯"
    tooltip = note if has_note else "Add note"
    
    # Create unique key for this note
    note_key = f"note_{payment_id}"
    
    # Use native Streamlit button with icon
    if st.button(
        icon_content,
        key=note_key,
        help=tooltip,
        use_container_width=True
    ):
        notes_state = st.session_state.notes_state
        
        # Close any open forms when opening a note
        if ui_manager and not notes_state['active_note']:
            ui_manager.close_all_dialogs()
        
        # Auto-save previous note if exists
        if notes_state['active_note'] and notes_state['active_note'] != payment_id:
            prev_id = notes_state['active_note']
            if prev_id in notes_state['edited_notes']:
                update_payment_note(prev_id, notes_state['edited_notes'][prev_id])
                notes_state['edited_notes'].pop(prev_id)
        
        # Toggle note state
        old_active = notes_state['active_note']
        if notes_state['active_note'] == payment_id:
            if payment_id in notes_state['edited_notes']:
                update_payment_note(payment_id, notes_state['edited_notes'][payment_id])
                notes_state['edited_notes'].pop(payment_id)
            notes_state['active_note'] = None
        else:
            notes_state['active_note'] = payment_id

def show_payment_history(client_id: int, ui_manager: UIStateManager) -> None:
    """Display payment history with efficient layout and smart navigation."""
    # Initialize all required states
    init_notes_state()
    init_filter_state()
    
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
        selected_filter = st.radio(
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
                selected_year = st.selectbox(
                    "Select Year",
                    options=years,
                    index=years.index(st.session_state.filter_state['year']) if st.session_state.filter_state['year'] in years else 0,
                    key="filter_year",
                    label_visibility="collapsed",
                    on_change=lambda: update_filter_state('year', st.session_state.filter_year)
                )
            
            with col2:
                selected_quarter = st.selectbox(
                    "Select Quarter",
                    options=["All Quarters", "Q1", "Q2", "Q3", "Q4"],
                    index=0,
                    key="filter_quarter",
                    label_visibility="collapsed",
                    on_change=lambda: update_filter_state('quarter', st.session_state.filter_quarter)
                )
    
    with middle_col:
        if st.button("Add Payment", type="primary", use_container_width=True):
            st.session_state.ui_manager = ui_manager
            initial_data = {
                'received_date': datetime.now().strftime('%Y-%m-%d')
            }
            ui_manager.open_payment_dialog(client_id=client_id, initial_data=initial_data)
            show_payment_dialog(client_id)
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
    
    # Add CSS for payment rows
    st.markdown("""
        <style>
        div.payment-table div[data-testid="column"] > div > div > div > div {
            padding: 0;
            margin: 0;
            line-height: 0.8;
        }
        
        div.payment-table div[data-testid="column"]:last-child button {
            padding: 0 !important;
            min-height: 24px !important;
            height: 24px !important;
            line-height: 24px !important;
            width: 24px !important;
            margin: 0 auto !important;
        }
        
        div.payment-table p {
            margin: 0;
            padding: 0;
            line-height: 1;
        }
        
        div.payment-table div[data-testid="stHorizontalBlock"] {
            margin-bottom: 0.1rem;
        }

        /* Note button styling */
        div.payment-table div[data-testid="column"]:nth-last-child(2) button {
            background: none !important;
            border: none !important;
            padding: 0 !important;
            min-height: 24px !important;
            height: 24px !important;
            line-height: 24px !important;
            width: 24px !important;
            margin: 0 auto !important;
            color: #1E90FF !important;
        }
        
        div.payment-table div[data-testid="column"]:nth-last-child(2) button:hover {
            color: #0056b3 !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="payment-table">', unsafe_allow_html=True)
    
    # Display headers
    header_cols = st.columns([1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1, 1])
    headers = ["Provider", "Period", "Frequency", "Method", "Received", "Total Assets", 
              "Expected Fee", "Actual Fee", "Discrepancy", "Notes", "Actions"]
    
    for col, header in zip(header_cols, headers):
        with col:
            st.markdown(f"<p style='font-weight: bold; margin: 0;'>{header}</p>", 
                       unsafe_allow_html=True)
    
    st.markdown("<hr style='margin: 0.1rem 0; border-color: #eee;'>", 
                unsafe_allow_html=True)
    
    # Display data rows
    for row in table_data:
        with st.container():
            cols = st.columns([1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1, 1])
            
            # Display payment data
            for i, (col, value) in enumerate(zip(cols[:-2], 
                ["Provider", "Period", "Frequency", "Method", "Received", "Total Assets",
                 "Expected Fee", "Actual Fee", "Discrepancy"])):
                with col:
                    st.markdown(f"<p style='margin: 0;'>{row[value]}</p>", 
                              unsafe_allow_html=True)
            
            # Notes column
            with cols[-2]:
                render_note_cell(
                    row['payment_id'],
                    row['Notes'],
                    provider=row['Provider'],
                    period=row['Period'],
                    ui_manager=ui_manager
                )
            
            # Actions column
            with cols[-1]:
                action_cols = st.columns([1, 1])
                with action_cols[0]:
                    if st.button("✏️", key=f"edit_{row['payment_id']}", help="Edit payment"):
                        payment_data = get_payment_by_id(row['payment_id'])
                        if payment_data:
                            initial_data = {
                                'payment_id': row['payment_id'],
                                'received_date': payment_data[0],
                                'applied_start_quarter': payment_data[1],
                                'applied_start_year': payment_data[2],
                                'applied_end_quarter': payment_data[3],
                                'applied_end_year': payment_data[4],
                                'total_assets': format_currency_ui(payment_data[5]),
                                'actual_fee': format_currency_ui(payment_data[6]),
                                'method': payment_data[7],
                                'notes': payment_data[8]
                            }
                            ui_manager.open_payment_dialog(
                                client_id=client_id,
                                mode='edit',
                                initial_data=initial_data
                            )
                            st.rerun()
                
                with action_cols[1]:
                    if st.button("🗑️", key=f"delete_{row['payment_id']}", help="Delete payment"):
                        st.session_state.showing_delete_confirm_for_id = row['payment_id']
                        st.rerun()
            
            # After the row, show confirmation if this is the row being deleted
            if getattr(st.session_state, 'showing_delete_confirm_for_id', None) == row['payment_id']:
                with st.container():
                    cols = st.columns([6, 2, 2])
                    with cols[0]:
                        st.warning(f"Delete this payment for {row['Period']}?")
                    with cols[1]:
                        if st.button("Yes, Delete", key=f"confirm_delete_{row['payment_id']}", type="primary", use_container_width=True):
                            if delete_payment(row['payment_id']):
                                st.session_state.showing_delete_confirm_for_id = None
                                get_payment_history.clear()
                                st.success("Payment deleted successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to delete payment")
                    with cols[2]:
                        if st.button("Cancel", key=f"cancel_delete_{row['payment_id']}", use_container_width=True):
                            st.session_state.showing_delete_confirm_for_id = None
                            st.rerun()
            
            # Handle active note editing
            if (
                'notes_state' in st.session_state 
                and st.session_state.notes_state['active_note'] == row['payment_id']
            ):
                note_cols = st.columns([4, 12, 1])
                with note_cols[1]:
                    st.markdown("<div style='border-top: 1px solid #eee; padding-top: 0.5rem;'></div>", unsafe_allow_html=True)
                    edited_note = st.text_area(
                        f"Note for {row['Provider']} - {row['Period']}",
                        value=row['Notes'] or "",
                        key=f"note_textarea_{row['payment_id']}",
                        height=100,
                        placeholder="Enter note here..."
                    )
                    
                    save_cols = st.columns([6, 2, 2])
                    with save_cols[1]:
                        if st.button("Save", key=f"save_note_{row['payment_id']}", type="primary"):
                            update_payment_note(row['payment_id'], edited_note)
                            st.session_state.notes_state['active_note'] = None
                            get_payment_history.clear()
                            st.rerun()
                    with save_cols[2]:
                        if st.button("Cancel", key=f"cancel_note_{row['payment_id']}"):
                            st.session_state.notes_state['active_note'] = None
                            st.rerun()
        
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    ui_manager = UIStateManager()
    show_payment_history(None, ui_manager)
