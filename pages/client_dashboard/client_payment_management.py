import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from utils.utils import (
    get_payment_history,
    update_payment_note,
    get_clients,
    get_contacts,
    get_client_details,
    add_contact,
    update_contact,
    delete_contact,
    get_payment_year_quarters,
    get_payment_by_id,
    format_currency_ui,
    get_client_dashboard_data,
)
from utils.perf_logging import log_event
from utils.ui_state_manager import UIStateManager

# ============================================================================
# STATE MANAGEMENT
# ============================================================================

def init_filter_state():
    """Initialize payment history filter state"""
    if 'filter_state' not in st.session_state:
        st.session_state.filter_state = {
            'time_filter': 'All Time',  # 'All Time', 'This Year', 'Custom'
            'year': datetime.now().year,
            'quarter': None,
            'current_filters': None
        }

def update_filter_state(key: str, value: Any) -> None:
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

def init_notes_state():
    """Initialize centralized notes state management"""
    if 'notes_state' not in st.session_state:
        st.session_state.notes_state = {
            'active_note': None,
            'edited_notes': {},
            'temp_notes': {}
        }

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

# ============================================================================
# NOTE HANDLING
# ============================================================================

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

def render_note_cell(payment_id, note, provider=None, period=None, ui_manager=None):
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
        
        # Close any open forms when opening a note
        if ui_manager and not notes_state['active_note']:
            ui_manager.close_all_dialogs()
        
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
# If note is active for this payment, show the edit form
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


def show_payment_history(client_id: int, ui_manager: UIStateManager) -> None:
    """Display payment history with efficient layout and smart navigation.
    
    Args:
        client_id: The ID of the client whose payment history to show
        ui_manager: UIStateManager instance for coordinating UI states
    """
    # Initialize all required states
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
            initial_data = {
                'received_date': datetime.now().strftime('%Y-%m-%d')
            }
            ui_manager.open_payment_dialog(client_id=client_id, initial_data=initial_data)
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
        </style>
    """, unsafe_allow_html=True)
    
    # Wrap the payment table in a div with our specific class
    st.markdown('<div class="payment-table">', unsafe_allow_html=True)
    
    # Display headers with minimal spacing
    header_cols = st.columns([2, 2, 1, 2, 2, 2, 2, 2, 1, 1])
    headers = ["Provider", "Period", "Frequency", "Received", "Total Assets", 
              "Expected Fee", "Actual Fee", "Discrepancy", "Notes", "Actions"]
    
    for col, header in zip(header_cols, headers):
        with col:
            st.markdown(f"<p style='font-weight: bold; margin: 0;'>{header}</p>", 
                       unsafe_allow_html=True)
    
    # Single header divider with minimal spacing
    st.markdown("<hr style='margin: 0.1rem 0; border-color: #eee;'>", 
                unsafe_allow_html=True)
    
    # Display data rows
    for row in table_data:
        with st.container():
            cols = st.columns([2, 2, 1, 2, 2, 2, 2, 2, 1, 1])
            
            # Display payment data
            for i, (col, value) in enumerate(zip(cols[:-2], 
                ["Provider", "Period", "Frequency", "Received", "Total Assets",
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
                    if st.button("✏️", key=f"edit_{row['payment_id']}", 
                               help="Edit payment"):
                        payment_data = get_payment_by_id(row['payment_id'])
                        if payment_data:
                            ui_manager.open_payment_dialog(
                                client_id=client_id,
                                mode='edit',
                                initial_data={
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
                            )
                            st.rerun()
                
                with action_cols[1]:
                    if st.button("🗑️", key=f"delete_{row['payment_id']}", 
                               help="Delete payment"):
                        st.session_state.delete_payment_id = row['payment_id']
                        st.session_state.show_delete_confirm = True
                        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    # Initialize UI manager when running directly
    ui_manager = UIStateManager()
    show_payment_history(None, ui_manager)
