import streamlit as st
from utils import get_clients, get_active_contract, get_latest_payment, get_client_details

def render_quarterly_summary():
    st.title("Quarterly Summary")
    st.markdown("""
    <style>
        [data-testid="stExpander"] {
            width: 100% !important;
        }
    </style>
    """, unsafe_allow_html=True)

    clients = get_clients()
    
    for client_id, display_name in clients:
        with st.expander(f"📋 {display_name}"):
            active_contract = get_active_contract(client_id)
            latest_payment = get_latest_payment(client_id)
            
            if active_contract:
                contract_number, provider_name, num_people, payment_type, payment_schedule, fee_type, percent_rate, flat_rate = active_contract
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Contract Details**")
                    st.write(f"Contract #: {contract_number}")
                    st.write(f"Provider: {provider_name}")
                    st.write(f"Payment Type: {payment_type}")
                    st.write(f"Schedule: {payment_schedule}")
                    
                with col2:
                    st.markdown("**Fee Structure**")
                    if fee_type == 'percentage':
                        st.write(f"Rate: {percent_rate}")
                    else:
                        st.write(f"Rate: ${flat_rate}")
                    st.write(f"Number of People: {num_people}")
                
                if latest_payment:
                    st.markdown("**Latest Payment**")
                    actual_fee, received_date, total_assets, applied_start_quarter, applied_start_year = latest_payment
                    st.write(f"Amount: ${actual_fee:,.2f}")
                    st.write(f"Received: {received_date}")
                    st.write(f"Total Assets: ${total_assets:,.2f}")
                    st.write(f"Applied to: Q{applied_start_quarter} {applied_start_year}")
            else:
                st.warning("No active contract found for this client.") 