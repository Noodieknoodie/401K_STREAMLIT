"""
Payment table display and interaction handling for client dashboard.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from utils.utils import update_payment_note
from utils.perf_logging import log_event

def format_currency(value):
    """Format a number as currency."""
    try:
        if value is None or value == "":
            return "N/A"
        return f"${float(value):,.2f}"
    except (ValueError, TypeError):
        return "N/A"

def format_payment_data(payments):
    """Format payment data for display with consistent formatting."""
    table_data = []
    
    for payment in payments:
        provider_name = payment[0] or "N/A"
        
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

def init_notes_state():
    """Initialize centralized notes state management."""
    if 'notes_state' not in st.session_state:
        st.session_state.notes_state = {
            'active_note': None,
            'edited_notes': {},
            'temp_notes': {}  # For storing unsaved changes
        }

def display_payment_table(client_id, payments):
    """Display the payments table with interactive features."""
    # Initialize notes state
    init_notes_state()
    
    # Initialize delete confirmation state
    if 'delete_payment_id' not in st.session_state:
        st.session_state.delete_payment_id = None
    if 'show_delete_confirm' not in st.session_state:
        st.session_state.show_delete_confirm = False
    
    # Format payment data
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
    
    # Display data rows
    for index, row in df.iterrows():
        # Create a container for the entire row including potential note
        with st.container():
            # Create container for the row content
            with st.container():
                # First render the row with all columns
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
                        if 'active_note_id' in st.session_state and st.session_state.active_note_id == row['payment_id']:
                            st.session_state.active_note_id = None
                        else:
                            st.session_state.active_note_id = row['payment_id']
                        st.rerun()
                
                with row_cols[9]:
                    # Create a container for action buttons
                    with st.container():
                        # Add edit button
                        if st.button("✏️", key=f"edit_payment_{row['payment_id']}", help="Edit payment"):
                            st.session_state.payment_form = {
                                'is_visible': True,
                                'mode': 'edit',
                                'payment_id': row['payment_id']
                            }
                            st.rerun()
                        # Add delete button
                        if st.button("🗑️", key=f"delete_payment_{row['payment_id']}", help="Delete payment"):
                            st.session_state.delete_payment_id = row['payment_id']
                            st.session_state.show_delete_confirm = True
                            st.rerun()
            
            # Show delete confirmation if needed
            if (
                st.session_state.show_delete_confirm 
                and st.session_state.delete_payment_id == row['payment_id']
            ):
                with st.container():
                    confirm_cols = st.columns([7, 3])
                    with confirm_cols[1]:
                        st.markdown("""<div style="border-top: 1px solid #eee; padding-top: 0.25rem;"></div>""", unsafe_allow_html=True)
                        st.warning("Delete this payment?")
                        confirm_cols2 = st.columns(2)
                        with confirm_cols2[0]:
                            if st.button("Yes", key=f"confirm_delete_{row['payment_id']}", type="primary"):
                                # TODO: Add delete_payment function call here
                                st.session_state.delete_payment_id = None
                                st.session_state.show_delete_confirm = False
                                st.rerun()
                        with confirm_cols2[1]:
                            if st.button("No", key=f"cancel_delete_{row['payment_id']}"):
                                st.session_state.delete_payment_id = None
                                st.session_state.show_delete_confirm = False
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
    
    st.markdown('</div>', unsafe_allow_html=True)
