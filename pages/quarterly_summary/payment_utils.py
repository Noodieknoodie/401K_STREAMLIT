from datetime import datetime

def get_current_quarter():
    """Get the current quarter based on today's date"""
    return (datetime.now().month - 1) // 3 + 1

def get_quarter_range(year, quarter):
    """Get the date range for a specific quarter"""
    quarter_starts = {
        1: (1, 1),   # Jan 1
        2: (4, 1),   # Apr 1
        3: (7, 1),   # Jul 1
        4: (10, 1)   # Oct 1
    }
    quarter_ends = {
        1: (3, 31),  # Mar 31
        2: (6, 30),  # Jun 30
        3: (9, 30),  # Sep 30
        4: (12, 31)  # Dec 31
    }
    
    start_month, start_day = quarter_starts[quarter]
    end_month, end_day = quarter_ends[quarter]
    
    start_date = datetime(year, start_month, start_day)
    end_date = datetime(year, end_month, end_day)
    
    return start_date, end_date

def validate_quarter_range(start_quarter, start_year, end_quarter, end_year):
    """Validate that the quarter range is in arrears and logically valid"""
    current_quarter = get_current_quarter()
    current_year = datetime.now().year
    
    # Convert quarters to absolute quarters for comparison
    start_absolute = start_year * 4 + start_quarter
    end_absolute = end_year * 4 + end_quarter
    current_absolute = current_year * 4 + current_quarter
    
    # Ensure both start and end quarters are in arrears
    if start_absolute >= current_absolute or end_absolute >= current_absolute:
        return False
    
    # Ensure end is not before start
    if end_absolute < start_absolute:
        return False
    
    return True

def format_quarter_display(quarter, year):
    """Format quarter and year for display"""
    return f"Q{quarter} {year}"

def calculate_expected_fee(contract_data, total_assets):
    """Calculate expected fee based on contract terms and total assets"""
    if not contract_data or not total_assets:
        return None
    
    try:
        total_assets = float(str(total_assets).replace('$', '').replace(',', ''))
        
        if contract_data[4] == 'percentage' and contract_data[5]:  # fee_type == 'percentage'
            return total_assets * contract_data[5]  # percent_rate
        elif contract_data[4] == 'flat' and contract_data[6]:  # fee_type == 'flat'
            return contract_data[6]  # flat_rate
        
        return None
    except (ValueError, TypeError):
        return None 

def get_quarter_options():
    """Get available quarter options for payment selection, excluding current and future quarters"""
    current_quarter = get_current_quarter()
    current_year = datetime.now().year
    
    # Start from previous quarter
    prev_quarter = current_quarter - 1 if current_quarter > 1 else 4
    prev_year = current_year if current_quarter > 1 else current_year - 1
    
    # Generate options for the last 8 quarters (2 years)
    options = []
    quarter = prev_quarter
    year = prev_year
    
    for _ in range(8):  # Show last 8 quarters
        options.append(f"Q{quarter} {year}")
        quarter -= 1
        if quarter < 1:
            quarter = 4
            year -= 1
    
    return options

def parse_quarter_option(quarter_option):
    """Parse quarter option string into quarter and year"""
    if not quarter_option:
        return None, None
    
    try:
        quarter = int(quarter_option[1])  # Extract number after 'Q'
        year = int(quarter_option[-4:])  # Extract year
        return quarter, year
    except (ValueError, IndexError):
        return None, None