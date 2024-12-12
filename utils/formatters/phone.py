def format_phone_number_ui(number):
    """Format phone number for UI display: (XXX) XXX-XXXX"""
    if not number:
        return ""
    # Remove any non-digit characters
    digits = ''.join(filter(str.isdigit, number))
    
    # Progressive formatting as user types
    if len(digits) <= 3:
        return digits
    elif len(digits) <= 6:
        return f"({digits[:3]}) {digits[3:]}"
    elif len(digits) <= 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    return f"({digits[:3]}) {digits[3:6]}-{digits[6:10]}"

def format_phone_number_db(number):
    """Format phone number for database storage: XXX-XXX-XXXX"""
    if not number:
        return ""
    # Remove any non-digit characters
    digits = ''.join(filter(str.isdigit, number))
    if len(digits) == 10:
        return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
    return number 