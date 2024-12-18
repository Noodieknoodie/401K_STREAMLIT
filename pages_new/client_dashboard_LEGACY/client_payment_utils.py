from datetime import datetime

def get_current_period(schedule):
    """Get the current period (month or quarter) based on schedule"""
    current_month = datetime.now().month
    if schedule and schedule.lower() == 'monthly':
        return current_month
    return (current_month - 1) // 3 + 1  # Quarter

def get_period_options(schedule):
    """Get available period options based on payment schedule"""
    if not schedule:
        return []  # Return empty list for null schedule
        
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    is_monthly = schedule.lower() == 'monthly'
    current_period = current_month if is_monthly else (current_month - 1) // 3 + 1
    
    # Start from previous period
    if is_monthly:
        prev_period = current_month - 1 if current_month > 1 else 12
        prev_year = current_year if current_month > 1 else current_year - 1
        periods_to_show = 24  # Show last 24 months
        period_format = lambda p, y: f"{datetime(y, p, 1).strftime('%b')} {y}"
    else:
        prev_period = current_period - 1 if current_period > 1 else 4
        prev_year = current_year if current_period > 1 else current_year - 1
        periods_to_show = 8  # Show last 8 quarters
        period_format = lambda p, y: f"Q{p} {y}"
    
    # Generate options
    options = []
    period = prev_period
    year = prev_year
    
    for _ in range(periods_to_show):
        options.append(period_format(period, year))
        period -= 1
        if is_monthly and period < 1:
            period = 12
            year -= 1
        elif not is_monthly and period < 1:
            period = 4
            year -= 1
    
    return options

def parse_period_option(period_option, schedule):
    """Parse period option string into period and year based on schedule"""
    if not period_option or not schedule:
        return None, None
    
    try:
        if schedule.lower() == 'monthly':
            # Parse "MMM YYYY" format (e.g., "Jan 2024")
            date = datetime.strptime(period_option, "%b %Y")
            return date.month, date.year
        else:
            # Parse "QN YYYY" format (e.g., "Q1 2024")
            quarter = int(period_option[1])  # Extract number after 'Q'
            year = int(period_option[-4:])  # Extract year
            return quarter, year
    except (ValueError, IndexError):
        return None, None

def validate_period_range(start_period, start_year, end_period, end_year, schedule):
    """Validate that the period range is in arrears and logically valid"""
    if not schedule:
        return False
        
    is_monthly = schedule.lower() == 'monthly'
    periods_per_year = 12 if is_monthly else 4
    
    current_period = datetime.now().month if is_monthly else (datetime.now().month - 1) // 3 + 1
    current_year = datetime.now().year
    
    # Convert to absolute periods for comparison
    start_absolute = start_year * periods_per_year + start_period
    end_absolute = end_year * periods_per_year + end_period
    current_absolute = current_year * periods_per_year + current_period
    
    # Ensure both start and end periods are in arrears
    if start_absolute >= current_absolute or end_absolute >= current_absolute:
        return False
    
    # Ensure end is not before start
    if end_absolute < start_absolute:
        return False
    
    return True

def format_period_display(period, year, schedule):
    """Format period and year for display based on schedule"""
    if not schedule:
        return "N/A"
        
    if schedule.lower() == 'monthly':
        return datetime(year, period, 1).strftime("%b %Y")
    return f"Q{period} {year}"

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

def get_current_quarter():
    """Get the current quarter (1-4) based on current month."""
    return (datetime.now().month - 1) // 3 + 1

def get_previous_quarter(current_quarter, current_year):
    """Get the previous quarter and its year.
    
    Args:
        current_quarter (int): Current quarter (1-4)
        current_year (int): Current year
        
    Returns:
        tuple: (previous_quarter, previous_year)
    """
    if current_quarter == 1:
        return 4, current_year - 1
    return current_quarter - 1, current_year

def get_quarter_month_range(quarter, year):
    """Get the start and end months for a given quarter.
    
    Args:
        quarter (int): Quarter number (1-4)
        year (int): Year
        
    Returns:
        tuple: (start_month, end_month)
    """
    start_month = ((quarter - 1) * 3) + 1
    end_month = start_month + 2
    return start_month, end_month