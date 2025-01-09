# summary.py
import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
from .summary_data import get_summary_year_data, get_available_years
from .quarter_tracker import show_quarter_tracker, get_period_payments
from .summary_utils import (
    calculate_current_quarter, get_default_year,
    format_currency, format_growth, calculate_trend_direction,
    calculate_sparkline_data
)
from streamlit_extras.metric_cards import style_metric_cards
import plotly.graph_objects as go
import numpy as np

def render_metrics_section(summary_data: dict) -> None:
    """Render the top metrics section with enhanced measurements."""
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
    """Render the charts section with focused, actionable visualizations."""
    # Create three columns for charts
    chart_col1, chart_col2, chart_col3 = st.columns(3)
    
    with chart_col1:
        # Group clients by provider and calculate total revenue
        provider_data = []
        for client_id, quarterly in summary_data['quarterly_totals'].items():
            provider = quarterly.get('provider', 'Unspecified')
            revenue = summary_data['client_metrics'][client_id]['total_fees']
            provider_data.append({
                'Provider': provider,
                'Revenue': revenue,
                'Client': quarterly['name']
            })
        
        if provider_data:
            provider_df = pd.DataFrame(provider_data)
            provider_summary = provider_df.groupby('Provider').agg({
                'Revenue': 'sum',
                'Client': 'count'
            }).reset_index()
            provider_summary = provider_summary.sort_values('Revenue', ascending=True)
            
            # Create horizontal bar chart
            provider_chart = alt.Chart(provider_summary).mark_bar().encode(
                y=alt.Y('Provider:N', 
                       sort='-x',
                       title=None),
                x=alt.X('Revenue:Q',
                       title='Revenue ($)',
                       axis=alt.Axis(format='$,.0f')),
                color=alt.Color('Provider:N', legend=None),
                tooltip=[
                    alt.Tooltip('Provider:N'),
                    alt.Tooltip('Revenue:Q', format='$,.2f'),
                    alt.Tooltip('Client:Q', title='Client Count')
                ]
            ).properties(height=300)
            
            st.altair_chart(provider_chart, use_container_width=True)
    
    with chart_col2:
        # Analyze quarterly revenue patterns
        quarter_data = []
        quarters = ['Q1', 'Q2', 'Q3', 'Q4']
        
        # First pass: collect all quarterly revenues
        all_quarterly_revenues = []
        for client_id, quarterly in summary_data['quarterly_totals'].items():
            for q in quarters:
                if quarterly.get(q, 0) > 0:
                    all_quarterly_revenues.append(quarterly[q])
        
        # Calculate quartiles for meaningful categorization
        if all_quarterly_revenues:
            q75 = np.percentile(all_quarterly_revenues, 75)
            q25 = np.percentile(all_quarterly_revenues, 25)
            
            for q in quarters:
                quarter_payments = []
                for client_id, quarterly in summary_data['quarterly_totals'].items():
                    amount = quarterly.get(q, 0)
                    if amount > 0:
                        size_category = "Large" if amount >= q75 else "Small" if amount <= q25 else "Medium"
                        quarter_payments.append({
                            'Quarter': q,
                            'Amount': amount,
                            'Size': size_category
                        })
                
                if quarter_payments:
                    # Calculate statistics for each quarter
                    total = sum(p['Amount'] for p in quarter_payments)
                    count = len(quarter_payments)
                    quarter_data.append({
                        'Quarter': q,
                        'Total Revenue': total,
                        'Payment Count': count,
                        'Average Payment': total / count if count > 0 else 0,
                        'Large Payments': sum(1 for p in quarter_payments if p['Size'] == 'Large'),
                        'Medium Payments': sum(1 for p in quarter_payments if p['Size'] == 'Medium'),
                        'Small Payments': sum(1 for p in quarter_payments if p['Size'] == 'Small')
                    })
        
        if quarter_data:
            quarter_df = pd.DataFrame(quarter_data)
            
            # Create a stacked bar chart with payment distribution
            base = alt.Chart(quarter_df).encode(
                x=alt.X('Quarter:N', title=None)
            )
            
            # Stacked bars showing payment size distribution
            bars = base.mark_bar().encode(
                y=alt.Y('Total Revenue:Q',
                       title='Revenue ($)',
                       axis=alt.Axis(format='$,.0f')),
                tooltip=[
                    alt.Tooltip('Quarter:N'),
                    alt.Tooltip('Total Revenue:Q', format='$,.2f'),
                    alt.Tooltip('Payment Count:Q', title='Number of Payments'),
                    alt.Tooltip('Average Payment:Q', format='$,.2f', title='Average Payment'),
                    alt.Tooltip('Large Payments:Q', title='Large Payments (Top 25%)'),
                    alt.Tooltip('Medium Payments:Q', title='Medium Payments'),
                    alt.Tooltip('Small Payments:Q', title='Small Payments (Bottom 25%)')
                ]
            )
            
            # Add text labels for total revenue
            text = base.mark_text(
                align='center',
                baseline='bottom',
                dy=-5,
                color='white'
            ).encode(
                y=alt.Y('Total Revenue:Q'),
                text=alt.Text('Total Revenue:Q', format='$,.0f')
            )
            
            # Combine the visualizations
            chart = (bars + text).properties(height=300)
            
            st.altair_chart(chart, use_container_width=True)
    
    with chart_col3:
        # Create AUM vs Participants analysis
        client_metrics = []
        for client_id, metrics in summary_data['client_metrics'].items():
            quarterly = summary_data['quarterly_totals'][client_id]
            if metrics.get('avg_aum', 0) > 0 and metrics.get('avg_participants', 0) > 0:
                client_metrics.append({
                    'Client': quarterly['name'],
                    'AUM': metrics['avg_aum'],
                    'Participants': metrics['avg_participants'],
                    'Revenue': metrics['total_fees'],
                    'Fee Type': quarterly['fee_type'].title()
                })
        
        if client_metrics:
            metrics_df = pd.DataFrame(client_metrics)
            
            # Create scatter plot
            scatter_chart = alt.Chart(metrics_df).mark_circle().encode(
                x=alt.X('Participants:Q',
                       title='Number of Participants',
                       scale=alt.Scale(type='log')),
                y=alt.Y('AUM:Q',
                       title='Assets Under Management ($)',
                       axis=alt.Axis(format='$,.0f'),
                       scale=alt.Scale(type='log')),
                size=alt.Size('Revenue:Q',
                            title='Revenue',
                            scale=alt.Scale(range=[100, 1000])),
                color=alt.Color('Fee Type:N',
                              title='Fee Type'),
                tooltip=[
                    'Client',
                    alt.Tooltip('AUM:Q', format='$,.2f'),
                    alt.Tooltip('Participants:Q', format=','),
                    alt.Tooltip('Revenue:Q', format='$,.2f'),
                    'Fee Type'
                ]
            ).properties(height=300)
            
            st.altair_chart(scatter_chart, use_container_width=True)

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
        .section-spacer {
            height: 1rem;  /* Reduced from 2rem */
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
    render_metrics_section(summary_data)
    
    st.markdown("<div class='section-spacer'></div>", unsafe_allow_html=True)
    
    # Charts section
    render_charts(summary_data)
    
    st.markdown("<div class='section-spacer'></div>", unsafe_allow_html=True)
    
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
            # Show expanded metrics in four columns
            col1, col2, col3, col4 = st.columns(4)
            
            # Column 1: Contract & Provider Info
            with col1:
                st.metric(
                    "Contract Details",
                    f"{row['_provider']}",
                    f"Contract #{row['_contract_number']}",
                    help="Provider and contract number"
                )
            
            # Column 2: Payment Structure
            with col2:
                payment_info = f"{row['_schedule'].title()}"
                rate_info = f"{row['_rate']*100:.1f}%" if row['_fee_type'] == 'percentage' else format_currency(row['_rate'])
                st.metric(
                    "Payment Structure",
                    f"{row['_fee_type'].title()} Rate: {rate_info}",
                    payment_info,
                    help="Fee type, rate, and payment schedule"
                )
            
            # Column 3: Performance
            with col3:
                yoy_change = row['YoY Change']
                trend_icon = "↗️" if yoy_change > 0 else "↘️" if yoy_change < 0 else "➡️"
                st.metric(
                    "Performance",
                    format_currency(row['Total']),
                    f"{trend_icon} {yoy_change:+.1f}% YoY" if yoy_change is not None else "No prior year data",
                    help="Total revenue and year-over-year change"
                )
            
            # Column 4: Plan Stats
            with col4:
                aum_display = format_currency(row['_aum']) if row['_aum'] and row['_aum'] != 'N/A' else 'N/A'
                participants = row['_participants'] if row['_participants'] and row['_participants'] != 'N/A' else 'N/A'
                st.metric(
                    "Plan Statistics",
                    f"{participants} participants",
                    f"AUM: {aum_display}",
                    help="Number of participants and Assets Under Management"
                )
            
            # Add payment status information
            st.markdown("<div style='margin: 0.5rem 0;'></div>", unsafe_allow_html=True)
            status_col1, status_col2, status_col3, status_col4 = st.columns(4)
            
            # Get current quarter payment status
            current_quarter, current_year = calculate_current_quarter()
            payment_data = get_period_payments(current_quarter, current_year)
            
            # Find client's payment status
            client_status = None
            client_payment = None
            for status_list in ['complete', 'partial', 'outstanding']:
                for entry in payment_data[status_list]:
                    if entry['name'] == row['Client']:
                        client_status = status_list
                        client_payment = entry
                        break
                if client_status:
                    break
            
            # Payment Status
            with status_col1:
                status_icon = "✅" if client_status == 'complete' else "⚠️" if client_status == 'partial' else "❌"
                status_text = client_status.title() if client_status else "Unknown"
                st.metric(
                    f"Q{current_quarter} {current_year} Status",
                    f"{status_icon} {status_text}",
                    "Current Quarter",
                    help="Payment status for current quarter"
                )
            
            # Expected vs Received
            with status_col2:
                if client_payment:
                    expected = format_currency(client_payment['expected']) if client_payment['expected'] else 'N/A'
                    received = format_currency(client_payment['received']) if client_payment['received'] else '$0.00'
                    st.metric(
                        "Expected vs Received",
                        received,
                        f"Expected: {expected}",
                        help="Expected and received amounts for current quarter"
                    )
                else:
                    st.metric(
                        "Expected vs Received",
                        "N/A",
                        "No data available",
                        help="Expected and received amounts for current quarter"
                    )
            
            # Payment Schedule Progress
            with status_col3:
                if client_payment:
                    schedule = client_payment['schedule']
                    expected_count = 3 if schedule == 'monthly' else 1
                    progress = f"{client_payment['payment_count']}/{expected_count}"
                    st.metric(
                        "Payment Progress",
                        progress,
                        schedule.title(),
                        help="Number of payments received vs expected for the quarter"
                    )
                else:
                    st.metric(
                        "Payment Progress",
                        "N/A",
                        "No schedule data",
                        help="Number of payments received vs expected for the quarter"
                    )
            
            # Historical Compliance
            with status_col4:
                # Calculate compliance rate from previous quarters
                total_quarters = sum(1 for q in [row['Q1'], row['Q2'], row['Q3'], row['Q4']] if q > 0)
                if total_quarters > 0:
                    compliance_rate = f"{(total_quarters / 4) * 100:.0f}%"
                    st.metric(
                        "Payment History",
                        compliance_rate,
                        f"{total_quarters}/4 quarters",
                        help="Percentage of quarters with payments received this year"
                    )
                else:
                    st.metric(
                        "Payment History",
                        "N/A",
                        "No historical data",
                        help="Percentage of quarters with payments received this year"
                    )
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close table-rows
    st.markdown('</div>', unsafe_allow_html=True)  # Close table-container