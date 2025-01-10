# Client Metrics Module
import streamlit as st
from utils.utils import calculate_rate_conversions
from utils.client_data import (
    get_consolidated_client_data,
    get_client_details_optimized
)
from streamlit_extras.metric_cards import style_metric_cards
from utils.database import get_database_connection

def show_client_metrics(client_id: int) -> None:
    """Display the client metrics section of the dashboard using summary tables."""
    from utils.utils import ensure_summaries_initialized
    from utils.client_data import get_consolidated_client_data
    ensure_summaries_initialized()

    # Get consolidated data (optimized version)
    data = get_consolidated_client_data(client_id)
    if not data:
        return

    # Apply existing styling
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

    # Display metrics 
    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        
        # Client Info - No changes needed
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

        # Financial metrics - Now using summary data
        col1, col2, col3, col4 = st.columns(4)
        
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
                    from utils.utils import calculate_rate_conversions
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

        with col2:
            st.metric(
                "Payment Schedule",
                data['active_contract']['payment_schedule'].title() 
                if data['active_contract'] and data['active_contract']['payment_schedule'] 
                else "N/A",
                None
            )
        
        with col3:
            if data['latest_payment']:
                payment = data['latest_payment']
                last_payment = f"${payment['actual_fee']:,.2f}" if payment['actual_fee'] else "No payments"
                payment_date = payment['received_date']
            else:
                last_payment = "No payments"
                payment_date = None
                
            st.metric(
                "Last Payment",
                last_payment,
                payment_date
            )
        
        with col4:
            if data['latest_payment'] and data['latest_payment']['total_assets']:
                aum_value = f"${data['latest_payment']['total_assets']:,.2f}"
                aum_date = f"Q{data['latest_payment']['quarter']} {data['latest_payment']['year']}"
            else:
                aum_value = "Not available"
                aum_date = None
                
            st.metric(
                "Last Recorded AUM",
                aum_value,
                aum_date
            )

        # Apply consistent styling
        from streamlit_extras.metric_cards import style_metric_cards
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