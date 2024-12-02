import streamlit as st
from utils import (
    get_clients, get_client_details, get_contacts, get_all_contracts,
    get_payment_history, update_payment_note, calculate_rate_conversions
)

def render_client_dashboard():
    st.title("Client Dashboard")
    st.markdown("""
    <style>
        .contact-info {
            border-bottom: 1px solid #eee;
            padding: 8px 0;
            margin-bottom: 8px;
        }
        .contact-info:last-child {
            border-bottom: none;
        }
        .contact-name {
            font-weight: bold;
            color: #1f77b4;
        }
        .contact-detail {
            margin: 2px 0;
            color: #555;
        }
    </style>
    """, unsafe_allow_html=True)

    clients = get_clients()
    client_dict = {client_id: name for client_id, name in clients}
    
    if not st.session_state.get('selected_client'):
        st.session_state.selected_client = next(iter(client_dict.keys())) if client_dict else None

    selected_client = st.selectbox(
        "Select Client",
        options=list(client_dict.keys()),
        format_func=lambda x: client_dict[x],
        key="client_selector"
    )

    if selected_client:
        st.session_state.selected_client = selected_client
        client_details = get_client_details(selected_client)
        if client_details:
            display_name, full_name = client_details
            st.subheader(f"Client: {full_name}")

            tab1, tab2, tab3 = st.tabs(["📞 Contacts", "📄 Contracts", "💰 Payment History"])
            
            with tab1:
                contacts = get_contacts(selected_client)
                if contacts:
                    for contact in contacts:
                        contact_type, name, phone, email, fax, physical_addr, mailing_addr, contact_id = contact
                        st.markdown(f"""
                        <div class="contact-info">
                            <div class="contact-name">{name} ({contact_type})</div>
                            <div class="contact-detail">📱 {phone if phone else 'N/A'}</div>
                            <div class="contact-detail">📧 {email if email else 'N/A'}</div>
                            <div class="contact-detail">📠 {fax if fax else 'N/A'}</div>
                            <div class="contact-detail">📍 {physical_addr if physical_addr else 'N/A'}</div>
                            <div class="contact-detail">📫 {mailing_addr if mailing_addr else 'N/A'}</div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No contacts found for this client.")

            with tab2:
                contracts = get_all_contracts(selected_client)
                if contracts:
                    for contract in contracts:
                        (contract_id, active, contract_number, provider_name, start_date, 
                         fee_type, percent_rate, flat_rate, schedule, payment_type, 
                         num_people, notes) = contract
                        
                        with st.expander(
                            f"{'🟢' if active == 'TRUE' else '⚪'} Contract #{contract_number} - {provider_name}"
                        ):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write("**Contract Details**")
                                st.write(f"Start Date: {start_date}")
                                st.write(f"Payment Type: {payment_type}")
                                st.write(f"Schedule: {schedule}")
                                st.write(f"Number of People: {num_people}")
                            
                            with col2:
                                st.write("**Fee Structure**")
                                if fee_type == 'percentage':
                                    rate = percent_rate
                                else:
                                    rate = flat_rate
                                base_rate, conversions = calculate_rate_conversions(rate, fee_type, schedule)
                                st.write(f"Base Rate: {base_rate}")
                                if conversions:
                                    st.write(f"Conversions: {conversions}")
                            
                            if notes:
                                st.write("**Notes:**")
                                st.write(notes)
                else:
                    st.info("No contracts found for this client.")

            with tab3:
                payments = get_payment_history(selected_client)
                if payments:
                    for payment in payments:
                        (provider_name, start_q, start_y, end_q, end_y, schedule,
                         received_date, total_assets, expected_fee, actual_fee,
                         notes, payment_id) = payment
                        
                        period = f"Q{start_q} {start_y}"
                        if end_q and end_y:
                            period += f" - Q{end_q} {end_y}"
                        
                        with st.expander(f"💵 {period} - ${actual_fee:,.2f}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"Provider: {provider_name}")
                                st.write(f"Received: {received_date}")
                                st.write(f"Schedule: {schedule}")
                            
                            with col2:
                                st.write(f"Total Assets: ${total_assets:,.2f}")
                                if expected_fee:
                                    st.write(f"Expected Fee: ${expected_fee:,.2f}")
                                st.write(f"Actual Fee: ${actual_fee:,.2f}")
                            
                            note = st.text_area("Notes", value=notes if notes else "", key=f"note_{payment_id}")
                            if note != (notes if notes else ""):
                                update_payment_note(payment_id, note)
                                st.success("Note updated successfully!")
                else:
                    st.info("No payment history found for this client.") 