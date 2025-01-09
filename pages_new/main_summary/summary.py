# summary.py
import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
from .summary_data import get_summary_year_data, get_available_years
from .quarter_tracker import show_quarter_tracker
from .summary_utils import (
    calculate_current_quarter, get_default_year,
    format_currency, format_growth, calculate_trend_direction,
    calculate_sparkline_data
)
from streamlit_extras.metric_cards import style_metric_cards
import plotly.graph_objects as go

def render_metrics_section(summary_data: dict) -> None:
    """Render the top metrics section with enhanced measurements."""
    st.markdown('<div class="section-header">Key Metrics</div>', unsafe_allow_html=True)
    
    # Calculate all metrics first
    # Client stats
    total_clients = len(summary_data['quarterly_totals'])
    active_clients = summary_data['overall_metrics']['active_clients']
    
    # Participant stats
    clients_with_participants = sum(1 for client_id in summary_data['client_metrics'] 
                                  if summary_data['client_metrics'][client_id].get('avg_participants', 0) > 0)
    total_participants = sum(metrics.get('avg_participants', 0) 
                           for metrics in summary_data['client_metrics'].values())
    avg_participants = total_participants / clients_with_participants if clients_with_participants > 0 else 0
    
    # Revenue stats
    total_revenue = summary_data['overall_metrics']['total_fees']
    avg_quarterly_revenue = total_revenue / 4 if total_revenue > 0 else 0
    avg_revenue_per_client = total_revenue / active_clients if active_clients > 0 else 0
    
    # AUM stats
    clients_with_aum = sum(1 for client_id in summary_data['client_metrics'] 
                          if summary_data['client_metrics'][client_id].get('avg_aum', 0) > 0)
    total_aum = sum(metrics.get('avg_aum', 0) 
                   for metrics in summary_data['client_metrics'].values())
    avg_aum_per_client = total_aum / clients_with_aum if clients_with_aum > 0 else 0
    
    # Fee structure stats
    fee_types = {
        'percentage': 0,
        'flat': 0
    }
    for client_id, quarterly in summary_data['quarterly_totals'].items():
        fee_type = quarterly.get('fee_type', 'N/A')
        if fee_type == 'percentage':
            fee_types['percentage'] += 1
        elif fee_type == 'flat':
            fee_types['flat'] += 1
            
    # Largest plan stats
    max_aum_client = max(summary_data['client_metrics'].items(), 
                        key=lambda x: x[1].get('avg_aum', 0))
    max_participants_client = max(summary_data['client_metrics'].items(), 
                                key=lambda x: x[1].get('avg_participants', 0))
    
    largest_aum_name = summary_data['quarterly_totals'][max_aum_client[0]]['name']
    largest_participants_name = summary_data['quarterly_totals'][max_participants_client[0]]['name']
    
    # Create 2 rows with 5 columns each
    for row in range(2):
        cols = st.columns(5)
        
        if row == 0:
            # First row: Total Clients, Total Participants, Avg Participants, Avg Quarterly Revenue, Avg Revenue per Client
            with cols[0]:
                st.metric(
                    "Total Clients",
                    f"{total_clients}",
                    f"Active: {active_clients}",
                    help="Total number of clients in the system"
                )
            with cols[1]:
                st.metric(
                    "Total Participants",
                    f"{total_participants:,.0f}",
                    f"{clients_with_participants} reporting clients",
                    help="Total number of participants across all plans"
                )
            with cols[2]:
                st.metric(
                    "Avg Participants per Plan",
                    f"{avg_participants:,.0f}",
                    "Per Reporting Plan",
                    help="Average number of participants per plan (for clients reporting participants)"
                )
            with cols[3]:
                st.metric(
                    "Average Quarterly Revenue",
                    format_currency(avg_quarterly_revenue),
                    "Per Quarter",
                    help="Average revenue per quarter"
                )
            with cols[4]:
                st.metric(
                    "Avg Revenue per Client",
                    format_currency(avg_revenue_per_client),
                    "Per Active Client",
                    help="Average revenue per active client"
                )
        else:
            # Second row: Total AUM, Avg AUM per Client, Fee Structure, Largest Plan AUM, Largest Plan Participants
            with cols[0]:
                st.metric(
                    "Total AUM",
                    format_currency(total_aum),
                    f"{clients_with_aum} reporting clients",
                    help="Total Assets Under Management across all clients"
                )
            with cols[1]:
                st.metric(
                    "Avg AUM per Client",
                    format_currency(avg_aum_per_client),
                    "Per Reporting Client",
                    help="Average AUM per client (for clients reporting AUM)"
                )
            with cols[2]:
                st.metric(
                    "Fee Structure",
                    f"{fee_types['percentage']} / {fee_types['flat']}",
                    "Percentage / Flat Rate",
                    help="Distribution of fee types (percentage vs. flat rate)"
                )
            with cols[3]:
                st.metric(
                    "Largest Plan (AUM)",
                    format_currency(max_aum_client[1].get('avg_aum', 0)),
                    largest_aum_name,
                    help="Plan with the highest Assets Under Management"
                )
            with cols[4]:
                st.metric(
                    "Largest Plan (Participants)",
                    f"{max_participants_client[1].get('avg_participants', 0):,.0f}",
                    largest_participants_name,
                    help="Plan with the most participants"
                )
        
        # Apply consistent styling for all metrics
        style_metric_cards(
            background_color="rgba(38, 39, 48, 0.2)",
            border_size_px=1,
            border_color="rgba(128, 128, 128, 0.2)",
            border_radius_px=5,
            border_left_color="#00b0ff",  # Blue accent for all metrics
            box_shadow=True
        )

def render_charts(summary_data: dict) -> None:
    """Render the charts section."""
    st.markdown('<div class="section-header">Charts</div>', unsafe_allow_html=True)
    
    
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

def create_revenue_sparkline(q1, q2, q3, q4):
    """Create a compact revenue sparkline."""
    quarters = ['Q1', 'Q2', 'Q3', 'Q4']
    values = [q1, q2, q3, q4]
    
    fig = go.Figure()
    
    # Add the sparkline
    fig.add_trace(go.Scatter(
        x=quarters,
        y=values,
        mode='lines+markers',
        line=dict(color='#0068C9', width=2),
        marker=dict(
            color='#0068C9',
            size=6,
        ),
    ))
    
    # Clean minimal layout
    fig.update_layout(
        height=100,  # Much shorter height
        margin=dict(l=0, r=0, t=0, b=0, pad=0),  # Remove all margins
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
        plot_bgcolor='rgba(0,0,0,0)',   # Transparent plot area
        showlegend=False,
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showline=False,
            showticklabels=True,
            tickfont=dict(size=10)
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showline=False,
            showticklabels=False  # Hide Y axis labels for cleaner look
        ),
    )
    
    return fig

def show_main_summary():
    """Display the main summary page."""
    try:
        show_quarter_tracker()
    except Exception as e:
        st.sidebar.error("Error loading payment tracker. Please try refreshing the page.")
        st.sidebar.exception(e)
        
    if 'expanded_rows' not in st.session_state:
        st.session_state.expanded_rows = set()
        
    st.markdown("""
        <style>
        .section-header {
            font-size: 1.3rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: #ffffff;
        }
        .section-spacer {
            height: 2rem;
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
        </style>
    """, unsafe_allow_html=True)

    # Top controls
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
        current_quarter, display_year = calculate_current_quarter()
        st.markdown(
            f'<div class="info-banner">Currently collecting Q{current_quarter} {display_year} payments</div>',
            unsafe_allow_html=True
        )

    # Get and render data
    summary_data = get_summary_year_data(selected_year)
    
    # Key Metrics section
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    render_metrics_section(summary_data)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<div class='section-spacer'></div>", unsafe_allow_html=True)
    
    # Charts section
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    render_charts(summary_data)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<div class='section-spacer'></div>", unsafe_allow_html=True)
    
    # Client Performance Table section
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
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
            # Show only metrics, no chart
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Revenue", format_currency(row['Total']), delta_color="normal", delta=f"{row['YoY Change']:+.1f}%")
            with col2:
                st.metric("Contract Details", f"{row['_fee_type'].title()}", f"{row['_rate']*100:.1f}%" if row['_fee_type'] == 'percentage' else format_currency(row['_rate']))
            with col3:
                st.metric("Participants", str(row['_participants']), delta="AUM: N/A")
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close table-rows
    st.markdown('</div>', unsafe_allow_html=True)  # Close table-container
    st.markdown('</div>', unsafe_allow_html=True)  # Close section-container