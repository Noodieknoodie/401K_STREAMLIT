import streamlit as st
from utils.utils import (
    get_client_details, get_active_contract, get_latest_payment,
    calculate_rate_conversions
)

def show_client_metrics(client_id):
    """Display the client metrics section of the dashboard."""
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