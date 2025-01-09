# Client Metrics Module
import streamlit as st
from utils.utils import calculate_rate_conversions
from utils.client_data import (
    get_consolidated_client_data,
    get_client_details_optimized
)
from streamlit_extras.metric_cards import style_metric_cards

def show_client_metrics(client_id: int) -> None:
    """Display the client metrics section of the dashboard.
    
    Args:
        client_id (int): The ID of the client to display metrics for
    """
    # Get all data in a single query
    data = get_consolidated_client_data(client_id)
    if not data:
        return

    # Add CSS for consistent metric card styling
    st.markdown("""
        <style>
        div[data-testid="stMetric"] {
            background: rgba(38, 39, 48, 0.2);
            padding: 1rem;
            border-radius: 0.5rem;
            height: 120px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        div[data-testid="stMetricLabel"] {
            font-size: 0.9rem;
            margin-bottom: 0.5rem;
        }
        div[data-testid="stMetricValue"] {
            font-size: 1.5rem;
            margin-bottom: 1rem;
        }
        div[data-testid="stMetricDelta"] {
            min-height: 1.5rem;
            display: flex;
            align-items: center;
        }
        </style>
    """, unsafe_allow_html=True)

    # Compact container for metrics
    with st.container():
        # First row - Client and Contract Info
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                "Client Name", 
                data['client']['display_name'],
                data['client']['full_name'] if data['client']['full_name'] else None
            )
        with col2:
            st.metric(
                "Provider",
                data['active_contract']['provider_name'] if data['active_contract'] else "N/A",
                None
            )
        with col3:
            st.metric(
                "Contract #",
                data['active_contract']['contract_number'] if data['active_contract'] else "N/A",
                None
            )
        with col4:
            st.metric(
                "Participants",
                data['active_contract']['num_people'] if data['active_contract'] else "N/A",
                None
            )

        # Second row - Rate and Payment Info
        col1, col2, col3, col4 = st.columns(4)
        
        # Rate Display
        with col1:
            rate_value = 'N/A'
            rate_type = None
            rate_conversions = None
            
            if data['active_contract']:
                contract = data['active_contract']
                if contract['fee_type'] == 'percentage' and contract['percent_rate']:
                    rate_value = f"{contract['percent_rate']*100:.3f}%"
                elif contract['fee_type'] == 'flat' and contract['flat_rate']:
                    rate_value = f"${contract['flat_rate']:,.2f}"
                
                if rate_value != 'N/A':
                    rate_type = contract['fee_type'].title()
                    schedule = contract['payment_schedule']
                    rate_value, rate_conversions = calculate_rate_conversions(
                        rate_value, 
                        contract['fee_type'],
                        schedule
                    )
            
            st.metric(
                "Rate",
                rate_value,
                rate_conversions if rate_conversions else rate_type
            )

        # Payment Schedule
        with col2:
            st.metric(
                "Payment Schedule",
                data['active_contract']['payment_schedule'].title() 
                if data['active_contract'] and data['active_contract']['payment_schedule'] 
                else "N/A",
                None
            )
        
        # Last Payment
        with col3:
            last_payment = 'No payments'
            payment_date = None
            if data['latest_payment']:
                payment = data['latest_payment']
                if payment['actual_fee']:
                    last_payment = f"${payment['actual_fee']:,.2f}"
                    payment_date = payment['received_date']
            st.metric("Last Payment", last_payment, payment_date)
        
        # AUM Display
        with col4:
            aum_value = 'Not available'
            aum_date = None
            if data['latest_payment']:
                payment = data['latest_payment']
                if payment['total_assets']:
                    aum_value = f"${payment['total_assets']:,.2f}"
                    aum_date = f"Q{payment['quarter']} {payment['year']}"
            st.metric(
                "Last Recorded AUM",
                aum_value,
                aum_date
            )

        # Apply metric cards styling
        style_metric_cards(
            background_color="rgba(38, 39, 48, 0.2)",
            border_size_px=1,
            border_color="rgba(128, 128, 128, 0.2)",
            border_radius_px=5,
            border_left_color="#00b0ff",
            box_shadow=True
        )

if __name__ == "__main__":
    st.set_page_config(page_title="Client Metrics", layout="wide")
    # For testing
    show_client_metrics(1)