import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from utils.utils import get_database_connection, calculate_rate_conversions

def load_and_cache_data(year=None, refresh=False):
    """Loads and caches payment data, optionally filtered by year."""
    if refresh or 'cached_payments' not in st.session_state or (year and st.session_state.get('cached_year') != year):
        conn = get_database_connection()
        query = """
            SELECT
                p.payment_id,
                c.display_name,
                p.applied_start_quarter,
                p.applied_start_year,
                p.actual_fee,
                p.received_date,
                p.total_assets,
                p.expected_fee,
                p.notes,
                ctr.fee_type,
                ctr.flat_rate,
                ctr.percent_rate,
                ctr.payment_schedule
            FROM payments p
            JOIN clients c ON p.client_id = c.client_id
            JOIN contracts ctr ON p.contract_id = ctr.contract_id
        """

        params = ()
        if year:
             query += " WHERE p.applied_start_year = ?"
             params = (year,)
            
        payments_df = pd.read_sql_query(query, conn, params=params)
        conn.close()

        # Convert date columns and numerical columns
        payments_df['received_date'] = pd.to_datetime(payments_df['received_date'], errors='coerce').dt.date
        
        # Clean numeric columns - replace '-' with 0 and convert to float
        numeric_columns = ['actual_fee', 'total_assets', 'expected_fee', 'flat_rate', 'percent_rate']
        for col in numeric_columns:
            payments_df[col] = payments_df[col].replace(['-', ''], 0)
            payments_df[col] = pd.to_numeric(payments_df[col], errors='coerce').fillna(0)

        st.session_state['cached_payments'] = payments_df
        if year:
            st.session_state['cached_year'] = year
    return st.session_state['cached_payments'].copy()

def calculate_quarterly_summary(payments_df, year):
    """Calculates and aggregates quarterly payment summaries."""
    if payments_df.empty:
        return pd.DataFrame()
    
    # Filter for the specific year if provided
    if year:
        payments_df = payments_df[payments_df['applied_start_year'] == year]
        
    #Ensure 'applied_start_quarter' is numeric
    payments_df['applied_start_quarter'] = pd.to_numeric(payments_df['applied_start_quarter'], errors='coerce').fillna(0).astype(int)
   
    # Aggregate quarterly payments
    quarterly_payments = payments_df.groupby(['display_name', 'applied_start_quarter']).agg(
        total_actual_fee = pd.NamedAgg(column='actual_fee', aggfunc='sum'),
        total_expected_fee = pd.NamedAgg(column='expected_fee', aggfunc='sum'),
        payment_count = pd.NamedAgg(column='payment_id', aggfunc='count')
    ).reset_index()

    # Convert quarter to a categorical type to ensure proper sorting
    quarterly_payments['applied_start_quarter'] = pd.Categorical(quarterly_payments['applied_start_quarter'], categories=range(1, 5), ordered=True)
    
    # Create year-quarter string for sorting
    quarterly_payments['year_quarter'] = quarterly_payments.apply(lambda row: f"{year}-Q{row['applied_start_quarter']}", axis=1)

    # Sort the data by client name and then by quarter
    quarterly_payments = quarterly_payments.sort_values(by=['display_name','year_quarter'])
    
    # Calculate discrepancies and apply formatting
    quarterly_payments['discrepancy'] = quarterly_payments['total_actual_fee'] - quarterly_payments['total_expected_fee']
    quarterly_payments.rename(columns={'applied_start_quarter': 'Quarter'}, inplace=True)

    # Calculate full-year totals
    full_year_totals = quarterly_payments.groupby('display_name').agg(
        total_actual_fee_year = pd.NamedAgg(column='total_actual_fee', aggfunc='sum'),
        total_expected_fee_year = pd.NamedAgg(column='total_expected_fee', aggfunc='sum'),
        total_payments_year = pd.NamedAgg(column='payment_count', aggfunc='sum')
    ).reset_index()
    full_year_totals['discrepancy_year'] = full_year_totals['total_actual_fee_year'] - full_year_totals['total_expected_fee_year']

    # Merge the full-year totals into the main quarterly summary
    quarterly_payments = pd.merge(quarterly_payments, full_year_totals, on='display_name', how='left')

    # Calculate the running totals
    quarterly_payments['cumulative_actual_fee_year'] = quarterly_payments.groupby('display_name')['total_actual_fee'].cumsum()
    quarterly_payments['cumulative_expected_fee_year'] = quarterly_payments.groupby('display_name')['total_expected_fee'].cumsum()
    quarterly_payments['cumulative_discrepancy_year'] = quarterly_payments['cumulative_actual_fee_year'] - quarterly_payments['cumulative_expected_fee_year']

    # Create formatted columns
    quarterly_payments['total_actual_fee'] = quarterly_payments['total_actual_fee'].apply(lambda x: f"${x:,.2f}")
    quarterly_payments['total_expected_fee'] = quarterly_payments['total_expected_fee'].apply(lambda x: f"${x:,.2f}")
    quarterly_payments['discrepancy'] = quarterly_payments['discrepancy'].apply(lambda x: f"${x:,.2f}")
    
    quarterly_payments['total_actual_fee_year'] = quarterly_payments['total_actual_fee_year'].apply(lambda x: f"${x:,.2f}")
    quarterly_payments['total_expected_fee_year'] = quarterly_payments['total_expected_fee_year'].apply(lambda x: f"${x:,.2f}")
    quarterly_payments['discrepancy_year'] = quarterly_payments['discrepancy_year'].apply(lambda x: f"${x:,.2f}")
    
    quarterly_payments['cumulative_actual_fee_year'] = quarterly_payments['cumulative_actual_fee_year'].apply(lambda x: f"${x:,.2f}")
    quarterly_payments['cumulative_expected_fee_year'] = quarterly_payments['cumulative_expected_fee_year'].apply(lambda x: f"${x:,.2f}")
    quarterly_payments['cumulative_discrepancy_year'] = quarterly_payments['cumulative_discrepancy_year'].apply(lambda x: f"${x:,.2f}")
    
    return quarterly_payments

def display_summary_metrics(quarterly_summary, year):
    """Displays key summary metrics in a clean layout."""
    st.header(f"Financial Summary for {year}", divider='blue')

    if quarterly_summary.empty:
         st.info(f"No payment data available for {year}.")
         return

    # Calculate totals for the selected year
    total_actual_fees = quarterly_summary['total_actual_fee'].str.replace(r'[$,]', '', regex=True).astype(float).sum()
    total_expected_fees = quarterly_summary['total_expected_fee'].str.replace(r'[$,]', '', regex=True).astype(float).sum()
    total_discrepancy = total_actual_fees - total_expected_fees
    
    # Display metrics using Streamlit columns for a compact layout
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Total Actual Fees", value=f"${total_actual_fees:,.2f}")
    col2.metric(label="Total Expected Fees", value=f"${total_expected_fees:,.2f}")
    col3.metric(label="Total Discrepancy", value=f"${total_discrepancy:,.2f}")

def display_quarterly_table(quarterly_summary):
    """Displays a table of quarterly summary data."""
    if quarterly_summary.empty:
        st.info("No data to display.")
        return
    
    # Define what to display and set the column order
    columns_to_display = [
        'display_name', 'Quarter', 'total_actual_fee', 'total_expected_fee', 'discrepancy',
        'total_actual_fee_year', 'total_expected_fee_year', 'discrepancy_year',
        'cumulative_actual_fee_year', 'cumulative_expected_fee_year', 'cumulative_discrepancy_year'
    ]

    # Display the DataFrame with specified columns and formatting
    st.dataframe(
        quarterly_summary[columns_to_display],
        column_config={
            'display_name': st.column_config.TextColumn(
                "Client",
                width="medium",
                help="Client name"
            ),
            'Quarter': st.column_config.NumberColumn(
                "Quarter",
                width="small",
                help="Quarter number (1-4)"
            ),
            'total_actual_fee': st.column_config.TextColumn(
                "Actual Fee",
                width="medium"
            ),
            'total_expected_fee': st.column_config.TextColumn(
                "Expected Fee",
                width="medium"
            ),
            'discrepancy': st.column_config.TextColumn(
                "Discrepancy",
                width="medium"
            ),
            'total_actual_fee_year': st.column_config.TextColumn(
                "Total Actual Fee (Year)",
                width="medium"
            ),
            'total_expected_fee_year': st.column_config.TextColumn(
                "Total Expected Fee (Year)",
                width="medium"
            ),
            'discrepancy_year': st.column_config.TextColumn(
                'Total Discrepancy (Year)',
                width="medium"
            ),
            'cumulative_actual_fee_year': st.column_config.TextColumn(
                "Cumulative Actual Fee",
                width="medium"
            ),
            'cumulative_expected_fee_year': st.column_config.TextColumn(
                "Cumulative Expected Fee",
                width="medium"
            ),
            'cumulative_discrepancy_year': st.column_config.TextColumn(
                "Cumulative Discrepancy",
                width="medium"
            )
        },
        hide_index=True,
        use_container_width=True
    )

def show_main_summary():
    """Main function to display the quarterly summary dashboard."""
    st.title("📊 Payment Analytics Dashboard")

    # Get available years from the data
    all_data = load_and_cache_data()
    available_years = sorted(all_data['applied_start_year'].dropna().unique(), reverse=True)
    
    if not available_years:
        st.warning("No payment data found in the database.")
        return
        
    # Default to the most recent year with data
    current_year = datetime.now().year
    default_year = available_years[0] if available_years else current_year
    
    # Year selector
    year = st.selectbox(
        "Select Year",
        options=available_years,
        index=0,
        help="Select a year to view payment data"
    )
    
    # Load data for the selected year
    payments_df = all_data[all_data['applied_start_year'] == year].copy()

    # Calculate and display summary data
    quarterly_summary = calculate_quarterly_summary(payments_df, year)
    display_summary_metrics(quarterly_summary, year)
    display_quarterly_table(quarterly_summary)
