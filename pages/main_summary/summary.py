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

def render_metrics_section(summary_data: dict) -> None:
    """Render the top metrics section and trend charts."""
    st.markdown("### Key Metrics")
    
    # Create a container for metrics
    metrics_container = st.container()
    with metrics_container:
        metrics_cols = st.columns(3)
        
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

    # Revenue Analysis Section
    st.markdown("### Revenue Analysis")
    trend_cols = st.columns([2, 1])
    
    with trend_cols[0]:
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
            chart = alt.Chart(trend_df).mark_bar().encode(
                x='Quarter:N',
                y=alt.Y('sum(Revenue):Q', title='Revenue'),
                color=alt.Color('Client:N', legend=None),
                tooltip=['Quarter', 'Client', alt.Tooltip('Revenue:Q', format='$,.2f')]
            ).properties(
                height=300,
                title='Quarterly Revenue Distribution'
            )
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("No revenue data available for selected year.")
            
    with trend_cols[1]:
        fee_types = {}
        for client_data in summary_data['quarterly_totals'].values():
            fee_type = client_data['fee_type']
            if fee_type:
                fee_types[fee_type] = fee_types.get(fee_type, 0) + 1
                
        if fee_types:
            pie_data = pd.DataFrame(
                {'Type': list(fee_types.keys()), 'Count': list(fee_types.values())}
            )
            pie_chart = alt.Chart(pie_data).mark_arc().encode(
                theta='Count:Q',
                color='Type:N',
                tooltip=['Type', 'Count']
            ).properties(
                height=200,
                title='Fee Type Distribution'
            )
            st.altair_chart(pie_chart, use_container_width=True)

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
    # Initialize session state
    if 'expanded_rows' not in st.session_state:
        st.session_state.expanded_rows = set()
    
    # Top controls section
    col1, col2, _ = st.columns([2, 3, 2])
    
    # Get available years and default year
    available_years = get_available_years()
    if not available_years:
        st.info("No payment data available.")
        return
        
    default_year = get_default_year()
    if default_year not in available_years:
        default_year = max(available_years)
    
    with col1:
        selected_year = st.selectbox(
            "Select Year",
            options=available_years,
            index=available_years.index(default_year),
            label_visibility="collapsed"
        )
    
    with col2:
        current_quarter = calculate_current_quarter()
        st.info(f"Currently collecting Q{current_quarter} {datetime.now().year} payments")
    
    # Get data
    summary_data = get_summary_year_data(selected_year)
    
    # Render metrics section using the existing function
    render_metrics_section(summary_data)
    
    # Client Performance section
    st.markdown("### Client Performance")
    
    # Create DataFrame with proper structure
    df = create_client_dataframe(summary_data)
    df = df.sort_values('Total', ascending=False)
    
    # Add minimal CSS for table styling
    st.markdown("""
        <style>
        div[data-testid="column"] {
            border-right: 1px solid #262730;
            padding: 0.5rem;
            display: flex;
            align-items: center;
        }
        div[data-testid="column"]:last-child {
            border-right: none;
        }
        div.stButton > button {
            width: 100%;
            text-align: left;
            padding: 0.5rem;
            background: none;
            border: none;
            line-height: 1.2;
            height: auto;
            min-height: 0;
            justify-content: flex-start;
        }
        div.stButton > button:hover {
            background: rgba(255, 255, 255, 0.05);
        }
        .header-text {
            font-weight: bold;
            padding: 0.5rem;
            line-height: 1.2;
        }
        .header-text.left-align {
            text-align: left;
        }
        .number-cell {
            text-align: right;
            line-height: 1.2;
            padding: 0.5rem;
        }
        hr {
            margin: 0 !important;
            padding: 0 !important;
        }
        /* Fix vertical alignment */
        div[data-testid="column"] > div {
            width: 100%;
        }
        div.stMarkdown p {
            margin: 0;
            line-height: 1.2;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Table headers
    header_cols = st.columns([1.5, 1, 1, 1, 1, 1])
    header_cols[0].markdown('<div class="header-text left-align">Client</div>', unsafe_allow_html=True)
    header_cols[1].markdown('<div class="header-text number-cell">Q1</div>', unsafe_allow_html=True)
    header_cols[2].markdown('<div class="header-text number-cell">Q2</div>', unsafe_allow_html=True)
    header_cols[3].markdown('<div class="header-text number-cell">Q3</div>', unsafe_allow_html=True)
    header_cols[4].markdown('<div class="header-text number-cell">Q4</div>', unsafe_allow_html=True)
    header_cols[5].markdown('<div class="header-text number-cell">Total</div>', unsafe_allow_html=True)
    
    st.markdown("<hr/>", unsafe_allow_html=True)
    
    # Display rows
    for _, row in df.iterrows():
        cols = st.columns([1.5, 1, 1, 1, 1, 1])
        
        # Client name and expand button
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
        
        # Quarterly values
        cols[1].markdown(f'<div class="number-cell">{format_currency(row["Q1"]) if row["Q1"] > 0 else "-"}</div>', unsafe_allow_html=True)
        cols[2].markdown(f'<div class="number-cell">{format_currency(row["Q2"]) if row["Q2"] > 0 else "-"}</div>', unsafe_allow_html=True)
        cols[3].markdown(f'<div class="number-cell">{format_currency(row["Q3"]) if row["Q3"] > 0 else "-"}</div>', unsafe_allow_html=True)
        cols[4].markdown(f'<div class="number-cell">{format_currency(row["Q4"]) if row["Q4"] > 0 else "-"}</div>', unsafe_allow_html=True)
        cols[5].markdown(f'<div class="number-cell">{format_currency(row["Total"])}</div>', unsafe_allow_html=True)
        
        # Show expanded details if row is expanded
        if row['Client'] in st.session_state.expanded_rows:
            with st.expander("", expanded=True):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Total Revenue",
                        format_currency(row['Total']),
                        format_growth(row['YoY Change'])
                    )
                
                with col2:
                    st.metric(
                        "Contract Details",
                        f"{row['_fee_type'].title()}",
                        f"{row['_rate']*100:.1f}%" if row['_fee_type'] == 'percentage' else format_currency(row['_rate'])
                    )
                
                with col3:
                    st.metric(
                        "Participants",
                        str(row['_participants']),
                        f"AUM: {format_currency(row['_aum'])}"
                    )
                
                # Show quarterly trend
                quarterly_data = pd.DataFrame({
                    'Quarter': ['Q1', 'Q2', 'Q3', 'Q4'],
                    'Revenue': [row['Q1'], row['Q2'], row['Q3'], row['Q4']]
                })
                
                chart = alt.Chart(quarterly_data).mark_bar().encode(
                    x=alt.X('Quarter:N', axis=alt.Axis(labelAngle=0)),
                    y=alt.Y('Revenue:Q', axis=alt.Axis(format='$,.0f')),
                    color=alt.value('#0068C9')
                ).properties(
                    height=200
                )
                
                st.altair_chart(chart, use_container_width=True)

if __name__ == "__main__":
    show_main_summary()