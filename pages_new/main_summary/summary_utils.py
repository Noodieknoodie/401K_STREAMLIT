from typing import Dict, List, Optional, Union, Sequence
import numpy as np
from datetime import datetime

def calculate_current_quarter() -> int:
    """Calculate current collection quarter based on arrears.
    
    Returns:
        int: Current quarter (1-4)
    """
    current_month = datetime.now().month
    return max(1, min(4, (current_month - 1) // 3 + 1))

def get_default_year() -> int:
    """Get default year based on current quarter.
    
    Returns:
        int: Default year for display
    """
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    # If we're in Q1 (Jan-Mar), we're collecting Q4 of previous year
    if current_month <= 3:
        return current_year - 1
    return current_year

def format_currency(value: Optional[float]) -> str:
    """Format currency value with consistent styling.
    
    Args:
        value: Amount to format
        
    Returns:
        str: Formatted currency string
    """
    if value is None or value == 0:
        return "N/A"
    try:
        return f"${float(value):,.2f}"
    except (ValueError, TypeError):
        return "N/A"

def format_growth(value: Optional[float]) -> str:
    """Format growth percentage with consistent styling.
    
    Args:
        value: Growth percentage to format
        
    Returns:
        str: Formatted growth string with sign
    """
    if value is None:
        return "N/A"
    try:
        value = float(value)
        return f"{value:+.1f}%" if value != 0 else "0.0%"
    except (ValueError, TypeError):
        return "N/A"

def calculate_trend_direction(
    current: float,
    previous: float,
    threshold: float = 5.0
) -> str:
    """Calculate trend direction and return appropriate icon.
    
    Args:
        current: Current value
        previous: Previous value
        threshold: Percentage change threshold for trend
        
    Returns:
        str: Trend indicator emoji
    """
    try:
        if previous == 0:
            return "➡️" if current == 0 else "⬆️"
        
        pct_change = ((current - previous) / abs(previous)) * 100
        
        if abs(pct_change) <= threshold:
            return "➡️"
        return "⬆️" if pct_change > 0 else "⬇️"
    except (ValueError, TypeError, ZeroDivisionError):
        return "➡️"

def calculate_sparkline_data(
    quarterly_data: Dict[str, float],
    min_value: Optional[float] = None,
    max_value: Optional[float] = None
) -> List[float]:
    """Calculate normalized sparkline data from quarterly values.
    
    Args:
        quarterly_data: Dictionary of quarterly values
        min_value: Optional minimum value for normalization
        max_value: Optional maximum value for normalization
        
    Returns:
        List[float]: Normalized values between 0 and 1
    """
    try:
        values = [
            float(quarterly_data.get(f'Q{i}', 0))
            for i in range(1, 5)
        ]
        
        if not any(values):
            return [0.0] * len(values)
            
        # Filter out zeros for min calculation if there are non-zero values
        non_zero_values = [v for v in values if v > 0]
        if not non_zero_values:
            return [0.0] * len(values)
            
        # Use provided min/max or calculate from values
        min_val = min_value if min_value is not None else min(non_zero_values)
        max_val = max_value if max_value is not None else max(values)
        
        if min_val == max_val:
            return [0.5 if v > 0 else 0.0 for v in values]
            
        return [
            (v - min_val) / (max_val - min_val) if v > 0 else 0.0
            for v in values
        ]
    except (ValueError, TypeError, ZeroDivisionError):
        return [0.0] * 4

def safe_divide(
    numerator: Optional[float],
    denominator: Optional[float]
) -> Optional[float]:
    """Safely divide two numbers, handling None and zero cases.
    
    Args:
        numerator: Number to divide
        denominator: Number to divide by
        
    Returns:
        Optional[float]: Result of division or None if invalid
    """
    try:
        if numerator is None or denominator is None:
            return None
        if denominator == 0:
            return None
        return numerator / denominator
    except (ValueError, TypeError):
        return None