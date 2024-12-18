import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
from .summary_data import get_summary_year_data, get_available_years
from .summary_utils import (
    calculate_current_quarter, get_default_year,
    format_currency, format_growth, calculate_trend_direction,
    calculate_sparkline_data
)
from streamlit_extras.metric_cards import style_metric_cards

def render_metrics_section(summary_data: dict) -> None:
    """Render the top metrics section and trend charts."""
    st.markdown('<div class="section-header">Key Metrics</div>', unsafe_allow_html=True)
    metrics_cols = st.columns([1, 1, 1])
    
    with metrics_cols[0]:
        st.metric(
            "Total Revenue",
            format_currency(summary_data['overall_metrics']['total_fees']),
            format_growth(summary_data['overall_metrics']['yoy_growth'])
        )
    with metrics_cols[1]:
        st.metric(
            "Active Clients",
            str(summary_data['overall_metrics']['active_clients']),
            None
        )
    with metrics_cols[2]:
        st.metric(
            "Avg Fee per Client",
            format_currency(summary_data['overall_metrics']['avg_fee_per_client']),
            None
        )
    
    # Apply the metric cards styling for dark theme
    style_metric_cards(
        background_color="rgba(38, 39, 48, 0.2)",
        border_size_px=1,
        border_color="rgba(128, 128, 128, 0.2)",
        border_radius_px=5,
        border_left_color="#00b0ff",
        box_shadow=True
    )

def create_client_dataframe(summary_data: dict) -> pd.DataFrame:
    """Create a DataFrame for the client performance table."""
    rows = []
    for client_id, quarterly in summary_data['quarterly_totals'].items():
        metrics = summary_data['client_metrics'][client_id]
        row = {
            'Client': quarterly['name'],
            'Q1': quarterly.get('Q1', 0),
            'Q2': quarterly.get('Q2', 0),
            'Q3': quarterly.get('Q3', 0),
            'Q4': quarterly.get('Q4', 0),
            'Total': metrics['total_fees'],
            'YoY Change': metrics.get('yoy_growth', 0),
            # Store additional data for expansion
            '_provider': quarterly.get('provider', 'N/A'),
            '_contract_number': quarterly.get('contract_number', 'N/A'),
            '_schedule': quarterly.get('schedule', 'N/A'),
            '_rate': quarterly.get('rate', 0),
            '_fee_type': quarterly.get('fee_type', 'N/A'),
            '_participants': metrics.get('avg_participants', 'N/A'),
            '_aum': metrics.get('avg_aum', 0)
        }
        rows.append(row)
    return pd.DataFrame(rows)

def show_main_summary():
    """Display the main summary page."""
    if 'expanded_rows' not in st.session_state:
        st.session_state.expanded_rows = set()
    
    # Add CSS for page-level constraints and styling
    st.markdown("""
        <style>
        .block-container {
            padding: 3rem 1rem 10rem;  
            max-width: 1200px !important;  
        }
        .table-container {
            width: 100%;
            max-width: 1000px;  
            margin: 0 auto;
        }
        .table-header {
            margin-top: 0.5rem;  
            padding: 0.5rem 0;
        }
        .table-header div[data-testid="column"] {
            border: none;
            padding-bottom: 0.25rem;
        }
        div.stButton > button {
            width: 100%;
            text-align: left !important;
            justify-content: flex-start !important;
            padding: 0.5rem;
            font-size: 0.9rem;
        }
        .info-banner {
            background: rgba(38, 39, 48, 0.1);
            padding: 0.4rem 0.8rem;
            width: fit-content;
            border-radius: 0.5rem;
            font-size: 0.9rem;
            height: 38px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: rgb(0, 176, 255);
            border: 1px solid rgba(0, 176, 255, 0.2);
        }
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
        .section-header {
            font-size: 1.3rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: #ffffff;
        }
        .section-spacer {
            height: 2rem;
        }
        div[data-testid="column"] {
            border-right: 1px solid rgba(38, 39, 48, 0.3);
            padding: 0.5rem 0.25rem;
            display: flex;
            align-items: center;
            min-height: 2.5rem;
        }
        div[data-testid="column"]:last-child {
            border-right: none;
        }
        .table-container {
            margin-top: 2rem;
        }
        .table-header {
            padding: 0;
            margin: 0;
        }
        .table-header div[data-testid="column"] {
            padding: 0.5rem 0.25rem;
        }
        hr {
            margin: 0 !important;
            padding: 0 !important;
            border-color: rgba(38, 39, 48, 0.3);
        }
        .table-rows {
            margin-top: 0.5rem;
        }
        div[data-testid="column"] > div[data-testid="stMarkdown"] {
            display: flex;
            align-items: center;
            height: 100%;
        }
        div.stButton > button:disabled {
            width: 100%;
            text-align: right !important;
            justify-content: flex-end !important;
            padding: 0.5rem;
            font-size: 0.9rem;
            font-family: monospace;
            background: none !important;
            border: none !important;
            color: white !important;
            cursor: default !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Page container for consistent spacing
    with st.container():
        # Top controls in a clean layout
        controls_cols = st.columns([1.5, 2.5, 1])
        
        available_years = get_available_years()
        if not available_years:
            st.info("No payment data available.")
            return
            
        default_year = get_default_year()
        if default_year not in available_years:
            default_year = max(available_years)
        
        with controls_cols[0]:
            selected_year = st.selectbox(
                "Select Year",
                options=available_years,
                index=available_years.index(default_year),
                label_visibility="collapsed"
            )
        
        with controls_cols[1]:
            current_quarter = calculate_current_quarter()
            st.markdown(
                f'<div class="info-banner">Currently collecting Q{current_quarter} {datetime.now().year} payments</div>',
                unsafe_allow_html=True
            )
    
    # Get and render data with spacing
    summary_data = get_summary_year_data(selected_year)
    st.markdown("<div class='section-spacer'></div>", unsafe_allow_html=True)
    
    # Key Metrics section
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    render_metrics_section(summary_data)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Revenue Analysis section
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="section-header">Revenue Analysis</div>', unsafe_allow_html=True)
        chart_cols = st.columns([2, 1])
        
        with chart_cols[0]:
            trend_data = []
            for client_id, quarterly in summary_data['quarterly_totals'].items():
                for q in range(1, 5):
                    if quarterly.get(f'Q{q}', 0) > 0:
                        trend_data.append({
                            'Quarter': f'Q{q}',
                            'Revenue': quarterly[f'Q{q}'],
                            'Client': quarterly['name']
                        })
            
            if trend_data:
                trend_df = pd.DataFrame(trend_data)
                # Create base chart with proper configuration
                base = alt.Chart(trend_df).encode(
                    x=alt.X('Quarter:N', axis=alt.Axis(labelAngle=0)),
                    y=alt.Y('sum(Revenue):Q', title='Revenue'),
                    color=alt.Color('Client:N', legend=None),
                    tooltip=['Quarter', 'Client', alt.Tooltip('Revenue:Q', format='$,.2f')]
                )
                
                # Apply the bar mark and configure the chart
                revenue_chart = base.mark_bar().properties(
                    height=250
                ).configure_view(
                    strokeWidth=0
                ).configure_axis(
                    grid=False,
                    domainColor='#57575740',
                    tickColor='#57575740'
                )
                
                st.altair_chart(revenue_chart, use_container_width=True)
            else:
                st.info("No revenue data available for selected year.")
        
        with chart_cols[1]:
            fee_types = {}
            for client_data in summary_data['quarterly_totals'].values():
                fee_type = client_data['fee_type']
                if fee_type:
                    fee_types[fee_type] = fee_types.get(fee_type, 0) + 1
            
            if fee_types:
                pie_data = pd.DataFrame({
                    'Type': list(fee_types.keys()),
                    'Count': list(fee_types.values())
                })
                
                # Create base pie chart with proper configuration
                base = alt.Chart(pie_data).encode(
                    theta='Count:Q',
                    color=alt.Color('Type:N', scale=alt.Scale(scheme='category10')),
                    tooltip=['Type', 'Count']
                )
                
                # Apply the arc mark and configure the chart
                pie_chart = base.mark_arc().properties(
                    height=250
                ).configure_view(
                    strokeWidth=0
                )
                
                st.altair_chart(pie_chart, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Client Performance section
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="section-header">Client Performance</div>', unsafe_allow_html=True)
        
        # Table container
        st.markdown('<div class="table-container">', unsafe_allow_html=True)
        
        # Headers first
        header_cols = st.columns([2, 1, 1, 1, 1, 1.2])
        header_cols[0].markdown('<div style="text-align: left;">Client</div>', unsafe_allow_html=True)
        header_cols[1].markdown('<div style="text-align: right;">Q1</div>', unsafe_allow_html=True)
        header_cols[2].markdown('<div style="text-align: right;">Q2</div>', unsafe_allow_html=True)
        header_cols[3].markdown('<div style="text-align: right;">Q3</div>', unsafe_allow_html=True)
        header_cols[4].markdown('<div style="text-align: right;">Q4</div>', unsafe_allow_html=True)
        header_cols[5].markdown('<div style="text-align: right;">Total</div>', unsafe_allow_html=True)
        
        # Divider immediately after headers
        st.markdown("<hr/>", unsafe_allow_html=True)
        
        # Create DataFrame with proper structure
        df = create_client_dataframe(summary_data)
        df = df.sort_values('Total', ascending=False)
        
        # Table rows with proper spacing
        st.markdown('<div class="table-rows">', unsafe_allow_html=True)
        for _, row in df.iterrows():
            cols = st.columns([2, 1, 1, 1, 1, 1.2])
            
            with cols[0]:
                if st.button(
                    f"{'▼' if row['Client'] in st.session_state.expanded_rows else '▶'} {row['Client']}", 
                    key=f"btn_{row['Client']}"
                ):
                    if row['Client'] in st.session_state.expanded_rows:
                        st.session_state.expanded_rows.remove(row['Client'])
                    else:
                        st.session_state.expanded_rows.add(row['Client'])
                    st.rerun()
            
            cols[1].button(format_currency(row["Q1"]) if row["Q1"] > 0 else "-", key=f"q1_{row['Client']}", disabled=True)
            cols[2].button(format_currency(row["Q2"]) if row["Q2"] > 0 else "-", key=f"q2_{row['Client']}", disabled=True)
            cols[3].button(format_currency(row["Q3"]) if row["Q3"] > 0 else "-", key=f"q3_{row['Client']}", disabled=True)
            cols[4].button(format_currency(row["Q4"]) if row["Q4"] > 0 else "-", key=f"q4_{row['Client']}", disabled=True)
            cols[5].button(format_currency(row["Total"]), key=f"total_{row['Client']}", disabled=True)
            
            if row['Client'] in st.session_state.expanded_rows:
                with st.expander("", expanded=True):
                    detail_cols = st.columns(3)
                    
                    with detail_cols[0]:
                        st.metric(
                            "Total Revenue",
                            format_currency(row['Total']),
                            format_growth(row['YoY Change'])
                        )
                    
                    with detail_cols[1]:
                        st.metric(
                            "Contract Details",
                            f"{row['_fee_type'].title()}",
                            f"{row['_rate']*100:.1f}%" if row['_fee_type'] == 'percentage' else format_currency(row['_rate'])
                        )
                    
                    with detail_cols[2]:
                        st.metric(
                            "Participants",
                            str(row['_participants']),
                            f"AUM: {format_currency(row['_aum'])}"
                        )
                    
                    # Quarterly trend chart
                    quarterly_data = pd.DataFrame({
                        'Quarter': ['Q1', 'Q2', 'Q3', 'Q4'],
                        'Revenue': [row['Q1'], row['Q2'], row['Q3'], row['Q4']]
                    })
                    
                    trend_chart = alt.Chart(quarterly_data).mark_bar().encode(
                        x=alt.X('Quarter:N', axis=alt.Axis(labelAngle=0)),
                        y=alt.Y('Revenue:Q', axis=alt.Axis(format='$,.0f')),
                        color=alt.value('#0068C9')
                    ).properties(
                        height=180
                    ).configure_axis(
                        grid=False
                    )
                    st.altair_chart(trend_chart, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)  # Close table-rows
        st.markdown('</div>', unsafe_allow_html=True)  # Close table-container
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    show_main_summary()