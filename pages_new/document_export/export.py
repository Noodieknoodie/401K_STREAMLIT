"""
Export Module
============

This module provides data export functionality for the 401K Payment Tracker.
It integrates with the existing database queries and follows the app's UI patterns.

Key Features:
- Export quarterly summaries (from main_summary)
- Export client payment histories (from client_payments)
- Multiple export formats (CSV/Excel)
- Consistent styling with main app
"""

import streamlit as st
from datetime import datetime
import pandas as pd
from io import BytesIO
from typing import Dict, Any, Optional, List
from utils.utils import (
    get_clients,
    get_payment_history,
    format_currency_ui,
)
from pages_new.main_summary.summary_data import (
    get_summary_year_data,
    get_available_years
)

def format_excel_workbook(writer: pd.ExcelWriter, df: pd.DataFrame, sheet_name: str) -> None:
    """Apply consistent Excel formatting exactly matching the app display."""
    try:
        workbook = writer.book
        worksheet = writer.sheets[sheet_name]
        
        # Define formats matching app display
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#262730',
            'font_color': 'white',
            'border': 1,
            'align': 'left',
            'font_size': 11
        })
        
        currency_format = workbook.add_format({
            'num_format': '$#,##0.00',
            'align': 'right',
            'font_size': 11
        })
        
        currency_large_format = workbook.add_format({
            'num_format': '$#,##0.00',
            'align': 'right',
            'font_size': 11
        })
        
        rate_format = workbook.add_format({
            'num_format': '0.000%',
            'align': 'right',
            'font_size': 11
        })
        
        yoy_format = workbook.add_format({
            'num_format': '+0.0%;-0.0%;0.0%',
            'align': 'right',
            'font_size': 11
        })
        
        date_format = workbook.add_format({
            'num_format': 'mmm dd, yyyy',
            'align': 'right',
            'font_size': 11
        })
        
        text_format = workbook.add_format({
            'align': 'left',
            'font_size': 11
        })
        
        # Write headers
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        # Auto-fit columns and apply formats
        for idx, col in enumerate(df.columns):
            series = df[col]
            max_len = max(
                series.astype(str).map(len).max(),
                len(str(series.name))
            ) + 2
            worksheet.set_column(idx, idx, max_len)
            
            col_lower = col.lower()
            
            if col_lower in {'q1', 'q2', 'q3', 'q4', 'total', 'actual fee', 'expected fee'}:
                worksheet.set_column(idx, idx, max_len, currency_format)
            elif col_lower == 'avg aum' or col_lower == 'total assets':
                worksheet.set_column(idx, idx, max_len, currency_large_format)
            elif col_lower == 'rate':
                worksheet.set_column(idx, idx, max_len, rate_format)
            elif col_lower == 'yoy change':
                worksheet.set_column(idx, idx, max_len, yoy_format)
            elif 'date' in col_lower:
                worksheet.set_column(idx, idx, max_len, date_format)
            else:
                worksheet.set_column(idx, idx, max_len, text_format)
            
            # Add conditional formatting for fee discrepancies if both columns exist
            if col_lower == 'actual fee' and 'Expected Fee' in df.columns:
                expected_col = df.columns.get_loc('Expected Fee')
                worksheet.conditional_format(1, idx, len(df), idx, {
                    'type': 'cell',
                    'criteria': 'not equal to',
                    'value': f'=INDIRECT("R[0]C[{expected_col-idx}]", FALSE)',
                    'format': workbook.add_format({'bg_color': '#FFF3E0'})
                })
    except Exception as e:
        st.error(f"Error formatting Excel workbook: {str(e)}")

def create_quarterly_summary_df(year_data: Dict[str, Any]) -> pd.DataFrame:
    """Create DataFrame for quarterly summary export."""
    try:
        rows = []
        for client_id, quarterly in year_data['quarterly_totals'].items():
            metrics = year_data['client_metrics'][client_id]
            row = {
                'Client': quarterly['name'],
                'Provider': quarterly.get('provider', 'N/A'),
                'Participants': metrics.get('avg_participants', 'N/A'),                
                'Contract #': quarterly.get('contract_number', 'N/A'),
                'Fee Type': quarterly.get('fee_type', 'N/A').title(),
                'Rate': quarterly.get('rate', 0),
                'Q1': quarterly.get('Q1', 0),
                'Q2': quarterly.get('Q2', 0),
                'Q3': quarterly.get('Q3', 0),
                'Q4': quarterly.get('Q4', 0),
                'Total': metrics['total_fees'],
            }
            rows.append(row)
        return pd.DataFrame(rows)
    except Exception as e:
        st.error(f"Error creating quarterly summary: {str(e)}")
        return pd.DataFrame()

def create_client_payments_df(payments: List[tuple]) -> pd.DataFrame:
    """Create DataFrame for client payments export."""
    try:
        formatted_data = []
        for payment in payments:
            row = {
                'Provider': payment[0] or "N/A",
                'Period Start': f"Q{payment[1]} {payment[2]}",
                'Period End': f"Q{payment[3]} {payment[4]}",
                'Method': payment[5].title() if payment[5] else "N/A",
                'Date Received': payment[6],
                'Total Assets': payment[7] or 0,
                'Expected Fee': payment[8] or 0,
                'Actual Fee': payment[9] or 0,
                'Notes': payment[10] or ""
            }
            formatted_data.append(row)
        return pd.DataFrame(formatted_data)
    except Exception as e:
        st.error(f"Error creating payments DataFrame: {str(e)}")
        return pd.DataFrame()

def export_data(df: pd.DataFrame, filename: str, file_format: str) -> Optional[BytesIO]:
    """Export DataFrame to specified format."""
    try:
        buffer = BytesIO()
        
        if file_format == 'csv':
            df.to_csv(buffer, index=False)
        else:  # Excel
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='Sheet1', index=False)
                format_excel_workbook(writer, df, 'Sheet1')
                
        buffer.seek(0)
        return buffer
    except Exception as e:
        st.error(f"Error exporting data: {str(e)}")
        return None

def show_export_section():
    """Display the export interface."""
    # Create a centered container for all content
    left_col, center_col, right_col = st.columns([1, 2, 1])
    
    with center_col:
        st.title("📥 Export Data")
        
        tab1, tab2 = st.tabs(["Quarterly Summary", "Client Payments"])
        
        with tab1:
            available_years = get_available_years()
            if not available_years:
                st.info("No payment data available for export.")
                return
                
            col1, col2 = st.columns([1, 1])
            
            with col1:
                year = st.selectbox(
                    "Select Year",
                    options=available_years,
                    index=0,
                    key="summary_year_select"
                )
            
            with col2:
                format_type = st.selectbox(
                    "File Format",
                    options=["Excel", "CSV"],
                    index=0,
                    key="summary_format_select"
                )
            
            # Generate button in its own row
            generate_clicked = st.button("Generate Report", type="primary", use_container_width=True, key="summary_generate_btn")
            
            if generate_clicked:
                try:
                    with st.spinner("Generating report..."):
                        year_data = get_summary_year_data(year)
                        df = create_quarterly_summary_df(year_data)
                        
                        if df.empty:
                            st.error("No data available for the selected year.")
                            return
                        
                        file_format = 'xlsx' if format_type == 'Excel' else 'csv'
                        buffer = export_data(df, f'quarterly_summary_{year}', file_format)
                        
                        if buffer:
                            st.download_button(
                                label="Download Report",
                                data=buffer,
                                file_name=f'quarterly_summary_{year}.{file_format}',
                                mime='application/vnd.ms-excel' if format_type == 'Excel' else 'text/csv',
                                use_container_width=True
                            )
                except Exception as e:
                    st.error(f"Error generating report: {str(e)}")
        
        with tab2:
            clients = get_clients()
            if not clients:
                st.info("No clients available.")
                return
                
            col1, col2 = st.columns([1, 1])
            
            with col1:
                client_names = ["Select a client..."] + [client[1] for client in clients]
                selected_name = st.selectbox(
                    "Select Client",
                    options=client_names,
                    index=0,
                    key="client_select"
                )
            
            with col2:
                format_type = st.selectbox(
                    "File Format",
                    options=["Excel", "CSV"],
                    index=0,
                    key="client_format_select"
                )
            
            # Generate button in its own row
            generate_clicked = st.button("Generate Report", 
                                       type="primary", 
                                       use_container_width=True, 
                                       key="client_generate_btn",
                                       disabled=(selected_name == "Select a client..."))
            
            if generate_clicked:
                try:
                    with st.spinner("Generating report..."):
                        client_id = next(
                            client[0] for client in clients 
                            if client[1] == selected_name
                        )
                        
                        payments = get_payment_history(client_id)
                        df = create_client_payments_df(payments)
                        
                        if df.empty:
                            st.error("No payment data available for the selected client.")
                            return
                        
                        file_format = 'xlsx' if format_type == 'Excel' else 'csv'
                        buffer = export_data(df, f'client_payments_{client_id}', file_format)
                        
                        if buffer:
                            st.download_button(
                                label="Download Report",
                                data=buffer,
                                file_name=f'{selected_name.replace(" ", "_")}_payments.{file_format}',
                                mime='application/vnd.ms-excel' if format_type == 'Excel' else 'text/csv',
                                use_container_width=True
                            )
                except Exception as e:
                    st.error(f"Error generating report: {str(e)}")

def show_export_data():
    """Main entry point for the export functionality."""
    show_export_section()

if __name__ == "__main__":
    show_export_data()