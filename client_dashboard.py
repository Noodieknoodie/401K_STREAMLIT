import streamlit as st
import pandas as pd
import time
from datetime import datetime
from utils import (
    get_clients, get_client_details, get_active_contract, 
    get_latest_payment, get_contacts, get_payment_history,
    calculate_rate_conversions, update_payment_note
)

def show_client_dashboard():
    """Render the client dashboard page"""
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
        # Reset expanders when client changes
        if st.session_state.selected_client != selected_client_name:
            st.session_state.selected_client = selected_client_name
            if 'expander_states' in st.session_state:
                del st.session_state.expander_states
        
        client_id = next(
            client[0] for client in clients if client[1] == selected_client_name
        )
        
        # Get all required data
        client_details = get_client_details(client_id)
        active_contract = get_active_contract(client_id)
        latest_payment = get_latest_payment(client_id)
        
        # Compact container for metrics
        with st.container():
            # First row - 4 columns
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Client Name", client_details[0], client_details[1] if client_details[1] else None)
            with col2:
                st.metric("Provider", active_contract[1] if active_contract and active_contract[1] else "N/A")
            with col3:
                st.metric("Contract #", active_contract[0] if active_contract and active_contract[0] else "N/A")
            with col4:
                st.metric("Participants", active_contract[2] if active_contract and active_contract[2] else "N/A")

            # Second row - 4 columns
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                rate_value = 'N/A'
                rate_type = None
                rate_conversions = None
                
                if active_contract and active_contract[5]:
                    if active_contract[5] == 'percentage':
                        if active_contract[6]:
                            rate_value = f"{active_contract[6]*100:.3f}%"
                    else:
                        if active_contract[7]:
                            rate_value = f"${active_contract[7]:,.2f}"
                    
                    if rate_value != 'N/A':
                        rate_type = active_contract[5].title()
                        schedule = active_contract[4] if active_contract[4] else None
                        rate_value, rate_conversions = calculate_rate_conversions(
                            rate_value, 
                            active_contract[5],
                            schedule
                        )
                
                st.metric(
                    "Rate", 
                    rate_value,
                    rate_conversions if rate_conversions else rate_type
                )
            
            with col2:
                st.metric("Payment Schedule", active_contract[4].title() if active_contract and active_contract[4] else "N/A")
            
            with col3:
                last_payment = 'No payments'
                payment_date = None
                if latest_payment and latest_payment[0]:
                    last_payment = f"${latest_payment[0]:,.2f}"
                    payment_date = latest_payment[1]
                st.metric("Last Payment", last_payment, payment_date)
            
            with col4:
                aum_value = 'Not available'
                aum_date = None
                if latest_payment and latest_payment[2]:
                    aum_value = f"${latest_payment[2]:,.2f}"
                    aum_date = f"Q{latest_payment[3]} {latest_payment[4]}"
                st.metric("Last Recorded AUM", aum_value, aum_date)

        # Small spacing before next section
        st.markdown("<div style='margin: 0.5rem 0;'></div>", unsafe_allow_html=True)
        
        # Create three equal-width columns for contact cards
        c1, c2, c3 = st.columns(3)
        
        contacts = get_contacts(client_id)
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
                st.button("Add Primary Contact", key="add_primary", use_container_width=True)
        
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
                st.button("Add Authorized Contact", key="add_authorized", use_container_width=True)
        
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
                st.button("Add Provider Contact", key="add_provider", use_container_width=True)

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
                icon_content = "💬" if has_note else "⭕"
                
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