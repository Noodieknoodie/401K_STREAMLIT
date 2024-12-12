def validate_phone_number(number):
    """Validate phone number format"""
    if not number:
        return True  # Empty is valid as field is optional
    digits = ''.join(filter(str.isdigit, number))
    return len(digits) == 10 