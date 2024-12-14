from datetime import datetime
from utils.debug_logger import debug

def get_current_period(schedule):
    """Get the current period (month or quarter) based on schedule"""
    current_month = datetime.now().month
    result = current_month if schedule and schedule.lower() == 'monthly' else (current_month - 1) // 3 + 1
    
    debug.log_ui_interaction(
        action="get_current_period",
        element="payment_utils",
        data={
            "schedule": schedule,
            "current_month": current_month,
            "result": result
        }
    )
    return result

def get_period_options(schedule):
    """Get available period options based on payment schedule"""
    if not schedule:
        debug.log_ui_interaction(
            action="get_period_options",
            element="payment_utils",
            data={
                "error": "no_schedule",
                "result": []
            }
        )
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
    
    debug.log_ui_interaction(
        action="get_period_options",
        element="payment_utils",
        data={
            "schedule": schedule,
            "is_monthly": is_monthly,
            "start_period": f"{prev_period}/{prev_year}",
            "options_count": len(options),
            "range": f"From {options[-1]} to {options[0]}"
        }
    )
    return options

def parse_period_option(period_option, schedule):
    """Parse period option string into period and year based on schedule"""
    if not period_option or not schedule:
        debug.log_ui_interaction(
            action="parse_period_option_error",
            element="payment_utils",
            data={
                "error": "missing_input",
                "period_option": period_option,
                "schedule": schedule
            }
        )
        return None, None
    
    try:
        if schedule.lower() == 'monthly':
            # Parse "MMM YYYY" format (e.g., "Jan 2024")
            date = datetime.strptime(period_option, "%b %Y")
            result = (date.month, date.year)
        else:
            # Parse "QN YYYY" format (e.g., "Q1 2024")
            quarter = int(period_option[1])  # Extract number after 'Q'
            year = int(period_option[-4:])  # Extract year
            result = (quarter, year)
            
        debug.log_ui_interaction(
            action="parse_period_option",
            element="payment_utils",
            data={
                "input": period_option,
                "schedule": schedule,
                "result": f"Period {result[0]} {result[1]}"
            }
        )
        return result
    except (ValueError, IndexError) as e:
        debug.log_ui_interaction(
            action="parse_period_option_error",
            element="payment_utils",
            data={
                "error": str(e),
                "period_option": period_option,
                "schedule": schedule
            }
        )
        return None, None

def validate_period_range(start_period, start_year, end_period, end_year, schedule):
    """Validate that the period range is in arrears and logically valid"""
    if not schedule:
        debug.log_ui_interaction(
            action="validate_period_range_error",
            element="payment_utils",
            data={"error": "no_schedule"}
        )
        return False
        
    is_monthly = schedule.lower() == 'monthly'
    periods_per_year = 12 if is_monthly else 4
    
    current_period = datetime.now().month if is_monthly else (datetime.now().month - 1) // 3 + 1
    current_year = datetime.now().year
    
    # Convert to absolute periods for comparison
    start_absolute = start_year * periods_per_year + start_period
    end_absolute = end_year * periods_per_year + end_period
    current_absolute = current_year * periods_per_year + current_period
    
    # Validate and log result
    is_valid = True
    reason = []
    
    # Ensure both start and end periods are in arrears
    if start_absolute >= current_absolute:
        is_valid = False
        reason.append("start_not_in_arrears")
    if end_absolute >= current_absolute:
        is_valid = False
        reason.append("end_not_in_arrears")
    
    # Ensure end is not before start
    if end_absolute < start_absolute:
        is_valid = False
        reason.append("end_before_start")
    
    debug.log_ui_interaction(
        action="validate_period_range",
        element="payment_utils",
        data={
            "start": f"Period {start_period} {start_year}",
            "end": f"Period {end_period} {end_year}",
            "schedule": schedule,
            "valid": is_valid,
            "reasons": reason if not is_valid else ["valid_range"]
        }
    )
    return is_valid

def format_period_display(period, year, schedule):
    """Format period and year for display based on schedule"""
    if not schedule:
        debug.log_ui_interaction(
            action="format_period_display_error",
            element="payment_utils",
            data={"error": "no_schedule"}
        )
        return "N/A"
        
    try:
        if schedule.lower() == 'monthly':
            result = datetime(year, period, 1).strftime("%b %Y")
        else:
            result = f"Q{period} {year}"
            
        debug.log_ui_interaction(
            action="format_period_display",
            element="payment_utils",
            data={
                "period": period,
                "year": year,
                "schedule": schedule,
                "result": result
            }
        )
        return result
    except ValueError as e:
        debug.log_ui_interaction(
            action="format_period_display_error",
            element="payment_utils",
            data={
                "error": str(e),
                "period": period,
                "year": year,
                "schedule": schedule
            }
        )
        return "N/A"

def calculate_expected_fee(contract_data, total_assets):
    """Calculate expected fee based on contract terms and total assets"""
    if not contract_data or not total_assets:
        debug.log_ui_interaction(
            action="calculate_fee_error",
            element="payment_utils",
            data={
                "error": "missing_input",
                "has_contract": bool(contract_data),
                "has_assets": bool(total_assets)
            }
        )
        return None
    
    try:
        total_assets = float(str(total_assets).replace('$', '').replace(',', ''))
        
        if contract_data[4] == 'percentage' and contract_data[5]:  # fee_type == 'percentage'
            result = total_assets * contract_data[5]  # percent_rate
        elif contract_data[4] == 'flat' and contract_data[6]:  # fee_type == 'flat'
            result = contract_data[6]  # flat_rate
        else:
            result = None
        
        debug.log_ui_interaction(
            action="calculate_expected_fee",
            element="payment_utils",
            data={
                "fee_type": contract_data[4],
                "total_assets": total_assets,
                "rate": contract_data[5] if contract_data[4] == 'percentage' else contract_data[6],
                "result": result
            }
        )
        return result
    except (ValueError, TypeError) as e:
        debug.log_ui_interaction(
            action="calculate_fee_error",
            element="payment_utils",
            data={
                "error": str(e),
                "total_assets_input": total_assets
            }
        )
        return None

def get_current_quarter():
    """Get the current quarter (1-4) based on current month."""
    result = (datetime.now().month - 1) // 3 + 1
    debug.log_ui_interaction(
        action="get_current_quarter",
        element="payment_utils",
        data={
            "month": datetime.now().month,
            "result": result
        }
    )
    return result

def get_previous_quarter(current_quarter, current_year):
    """Get the previous quarter and its year."""
    if current_quarter == 1:
        result = (4, current_year - 1)
    else:
        result = (current_quarter - 1, current_year)
        
    debug.log_ui_interaction(
        action="get_previous_quarter",
        element="payment_utils",
        data={
            "current": f"Q{current_quarter} {current_year}",
            "previous": f"Q{result[0]} {result[1]}"
        }
    )
    return result

def get_quarter_month_range(quarter, year):
    """Get the start and end months for a given quarter."""
    start_month = ((quarter - 1) * 3) + 1
    end_month = start_month + 2
    
    debug.log_ui_interaction(
        action="get_quarter_month_range",
        element="payment_utils",
        data={
            "quarter": quarter,
            "year": year,
            "start_month": start_month,
            "end_month": end_month
        }
    )
    return start_month, end_month