import unittest
from unittest.mock import patch, MagicMock
import streamlit as st
from freezegun import freeze_time
from datetime import datetime
import traceback
import sys

# Debug function to help identify test issues
def debug_test(func):
    def wrapper(*args, **kwargs):
        try:
            print(f"\nExecuting test: {func.__name__}")
            print("=" * 50)
            # Check if session state is properly initialized
            if not hasattr(st, 'session_state'):
                raise Exception("ERROR: st.session_state not initialized")
            
            # Print current session state for debugging
            print("Current session state variables:")
            for key, value in st.session_state.items():
                print(f"  {key}: {value}")
            
            result = func(*args, **kwargs)
            print(f"Test {func.__name__} completed successfully")
            return result
        except Exception as e:
            print(f"\nERROR in test {func.__name__}:")
            print("-" * 50)
            print(f"Exception type: {type(e).__name__}")
            print(f"Exception message: {str(e)}")
            print("\nTraceback:")
            traceback.print_exc()
            print("-" * 50)
            raise  # Re-raise the exception after printing debug info
    return wrapper

try:
    from pages_new.client_display_and_forms.client_payment_utils import (
        get_current_period,
        get_period_options,
        parse_period_option,
        validate_period_range,
        format_period_display,
        calculate_expected_fee
    )
except ImportError as e:
    print("\nERROR: Failed to import required modules")
    print(f"Import Error: {str(e)}")
    print("\nTraceback:")
    traceback.print_exc()
    sys.exit(1)

class TestClientPaymentUtils(unittest.TestCase):
    def setUp(self):
        print("\nSetting up test environment...")
        try:
            # Initialize complete session state
            if not hasattr(st, 'session_state'):
                st.session_state = {}
                
            # Initialize all required state variables
            required_states = {
                'payment_edit_id': None,
                'show_payment_form': False,
                'payment_form_data': {},
                'client_id': 1,
                'current_page': '👥 Client Dashboard',
                'selected_client': None,
                'client_selector_dashboard': None,
                'previous_client': None,
                'show_contract_form': False,
                'contract_form_data': {}
            }
            
            for key, value in required_states.items():
                st.session_state[key] = value
                if key not in st.session_state:
                    raise Exception(f"Failed to initialize session state: {key}")
                    
            print("Session state initialized successfully")
            
        except Exception as e:
            print("\nERROR in setUp:")
            print(f"Exception: {str(e)}")
            print("\nTraceback:")
            traceback.print_exc()
            raise

    @debug_test
    @freeze_time("2024-03-15")  # Fix time to March 15, 2024
    def test_get_current_period(self):
        """Test current period calculation for monthly and quarterly schedules"""
        try:
            # Test None/empty schedule first (edge cases)
            self.assertEqual(get_current_period(None), 1)  # Q1 for March
            self.assertEqual(get_current_period(''), 1)    # Q1 for March
            self.assertEqual(get_current_period('invalid'), 1)  # Q1 for March
            
            # Monthly periods with proper case handling
            self.assertEqual(get_current_period('monthly'), 3)
            self.assertEqual(get_current_period('MONTHLY'), 3)
            self.assertEqual(get_current_period('Monthly'), 3)
            
            # Quarterly periods with proper case handling
            self.assertEqual(get_current_period('quarterly'), 1)
            self.assertEqual(get_current_period('QUARTERLY'), 1)
            self.assertEqual(get_current_period('Quarterly'), 1)
            
            # Test all months with freeze_time
            test_dates = [
                ("2024-01-15", 1, 1),   # January
                ("2024-02-15", 2, 1),   # February
                ("2024-03-15", 3, 1),   # March
                ("2024-04-15", 4, 2),   # April
                ("2024-05-15", 5, 2),   # May
                ("2024-06-15", 6, 2),   # June
                ("2024-07-15", 7, 3),   # July
                ("2024-08-15", 8, 3),   # August
                ("2024-09-15", 9, 3),   # September
                ("2024-10-15", 10, 4),  # October
                ("2024-11-15", 11, 4),  # November
                ("2024-12-15", 12, 4)   # December
            ]
            
            for test_date, expected_month, expected_quarter in test_dates:
                print(f"\nTesting date: {test_date}")
                with freeze_time(test_date):
                    try:
                        self.assertEqual(
                            get_current_period('monthly'),
                            expected_month,
                            f"Monthly: Failed for {test_date}, expected {expected_month}"
                        )
                        self.assertEqual(
                            get_current_period('quarterly'),
                            expected_quarter,
                            f"Quarterly: Failed for {test_date}, expected Q{expected_quarter}"
                        )
                    except Exception as e:
                        print(f"Error testing date {test_date}:")
                        print(str(e))
                        raise
                        
        except Exception as e:
            print("\nError in test_get_current_period:")
            print(str(e))
            print("\nTraceback:")
            traceback.print_exc()
            raise

    @debug_test
    @freeze_time("2024-03-15")
    def test_get_period_options(self):
        """Test period options generation for different schedules"""
        try:
            # Test None/empty schedule first (edge cases)
            self.assertEqual(get_period_options(None), [])
            self.assertEqual(get_period_options(''), [])
            
            # Test monthly schedule (should show last 24 months)
            with patch('streamlit.selectbox') as mock_selectbox:
                print("\nTesting monthly schedule...")
                try:
                    mock_selectbox.return_value = 'Feb 2024'
                    monthly_options = get_period_options('monthly')
                    self.assertEqual(len(monthly_options), 24)
                    self.assertEqual(monthly_options[0], 'Feb 2024')
                    self.assertEqual(monthly_options[-1], 'Mar 2022')
                    self.assertNotIn('Mar 2024', monthly_options)
                    self.assertNotIn('Apr 2024', monthly_options)
                except Exception as e:
                    print("Error in monthly schedule test:")
                    print(str(e))
                    raise
            
            # Test quarterly schedule
            with patch('streamlit.selectbox') as mock_selectbox:
                print("\nTesting quarterly schedule...")
                try:
                    mock_selectbox.return_value = 'Q4 2023'
                    quarterly_options = get_period_options('quarterly')
                    self.assertEqual(len(quarterly_options), 8)
                    self.assertEqual(quarterly_options[0], 'Q4 2023')
                    self.assertEqual(quarterly_options[-1], 'Q1 2022')
                    self.assertNotIn('Q1 2024', quarterly_options)
                    self.assertNotIn('Q2 2024', quarterly_options)
                except Exception as e:
                    print("Error in quarterly schedule test:")
                    print(str(e))
                    raise

        except Exception as e:
            print("\nError in test_get_period_options:")
            print(str(e))
            print("\nTraceback:")
            traceback.print_exc()
            raise

    @debug_test
    def test_parse_period_option(self):
        """Test period option parsing for different formats"""
        try:
            test_cases = [
                ('Jan 2024', 'monthly', (1, 2024)),
                ('Dec 2023', 'monthly', (12, 2023)),
                ('Q1 2024', 'quarterly', (1, 2024)),
                ('Q4 2023', 'quarterly', (4, 2023)),
                ('Invalid', 'monthly', (None, None)),
                ('Q5 2024', 'quarterly', (None, None)),
                ('Q0 2024', 'quarterly', (None, None)),
                ('Month 13 2024', 'monthly', (None, None)),
                ('', 'monthly', (None, None)),
                (None, 'quarterly', (None, None))
            ]

            for input_str, schedule, expected in test_cases:
                print(f"\nTesting parse_period_option: {input_str}, {schedule}")
                try:
                    result = parse_period_option(input_str, schedule)
                    self.assertEqual(
                        result, 
                        expected,
                        f"Failed for input: {input_str}, schedule: {schedule}"
                    )
                except Exception as e:
                    print(f"Error testing case: {input_str}, {schedule}")
                    print(str(e))
                    raise

        except Exception as e:
            print("\nError in test_parse_period_option:")
            print(str(e))
            print("\nTraceback:")
            traceback.print_exc()
            raise

    @debug_test
    @freeze_time("2024-03-15")
    def test_validate_period_range(self):
        """Test period range validation"""
        try:
            test_cases = [
                # (start_period, start_year, end_period, end_year, schedule, expected)
                (1, 2024, 1, 2024, 'monthly', True),
                (12, 2023, 1, 2024, 'monthly', True),
                (11, 2023, 1, 2024, 'monthly', True),
                (4, 2023, 4, 2023, 'quarterly', True),
                (3, 2023, 4, 2023, 'quarterly', True),
                (2, 2023, 4, 2023, 'quarterly', True),
                (3, 2024, 3, 2024, 'monthly', False),  # Current month
                (4, 2024, 4, 2024, 'monthly', False),  # Future month
                (1, 2024, 1, 2024, 'quarterly', False),  # Current quarter
                (2, 2024, 2, 2024, 'quarterly', False),  # Future quarter
                (2, 2024, 1, 2024, 'monthly', False),  # End before start
                (4, 2023, 3, 2023, 'quarterly', False),  # End before start
                (1, 2024, 1, 2024, None, False),  # Invalid schedule
                (1, 2024, 1, 2024, '', False),  # Empty schedule
            ]

            for start_p, start_y, end_p, end_y, schedule, expected in test_cases:
                print(f"\nTesting period range: {start_p}/{start_y} to {end_p}/{end_y} ({schedule})")
                try:
                    result = validate_period_range(start_p, start_y, end_p, end_y, schedule)
                    self.assertEqual(
                        result,
                        expected,
                        f"Failed for {start_p}/{start_y} to {end_p}/{end_y} ({schedule})"
                    )
                except Exception as e:
                    print(f"Error testing case: {start_p}/{start_y} to {end_p}/{end_y} ({schedule})")
                    print(str(e))
                    raise

        except Exception as e:
            print("\nError in test_validate_period_range:")
            print(str(e))
            print("\nTraceback:")
            traceback.print_exc()
            raise

    @debug_test
    def test_format_period_display(self):
        """Test period formatting for display"""
        try:
            test_cases = [
                (1, 2024, 'monthly', 'Jan 2024'),
                (12, 2023, 'monthly', 'Dec 2023'),
                (1, 2024, 'quarterly', 'Q1 2024'),
                (4, 2023, 'quarterly', 'Q4 2023'),
                (13, 2024, 'monthly', 'N/A'),
                (5, 2024, 'quarterly', 'N/A'),
                (1, 2024, None, 'N/A'),
                (1, 2024, '', 'N/A'),
            ]

            for period, year, schedule, expected in test_cases:
                print(f"\nTesting format_period_display: {period}, {year}, {schedule}")
                try:
                    result = format_period_display(period, year, schedule)
                    self.assertEqual(
                        result,
                        expected,
                        f"Failed for period: {period}, year: {year}, schedule: {schedule}"
                    )
                except Exception as e:
                    print(f"Error testing case: {period}, {year}, {schedule}")
                    print(str(e))
                    raise

        except Exception as e:
            print("\nError in test_format_period_display:")
            print(str(e))
            print("\nTraceback:")
            traceback.print_exc()
            raise

@debug_test
def test_calculate_expected_fee(self):
    """Test fee calculation based on contract terms"""
    print("\nStarting expected fee calculation tests...")

    try:
        # Setup test contracts
        contract_percentage = (1, 'Provider', '12345', 'monthly', 'percentage', 0.015, None, 100)
        contract_flat = (1, 'Provider', '12345', 'monthly', 'flat', None, 5000, 100)

        # Test percentage fee calculations
        with patch('streamlit.number_input') as mock_number_input:
            print("\nTesting percentage fee calculations...")
            mock_number_input.return_value = 1000000

            try:
                # Test basic percentage calculation
                result = calculate_expected_fee(contract_percentage, 1000000)
                self.assertEqual(result, 15000.0, "Basic percentage calculation failed")

                # Test formatted input strings
                result = calculate_expected_fee(contract_percentage, '1,000,000')
                self.assertEqual(result, 15000.0, "Failed with formatted number string")

                result = calculate_expected_fee(contract_percentage, '$1,000,000')
                self.assertEqual(result, 15000.0, "Failed with currency string")

                # Test large number
                result = calculate_expected_fee(contract_percentage, 1000000000)
                self.assertEqual(result, 15000000.0, "Failed with large number")

            except Exception as e:
                print("Error in percentage fee calculations:")
                print(str(e))
                traceback.print_exc()
                raise

        # Test flat fee calculations
        with patch('streamlit.number_input') as mock_number_input:
            print("\nTesting flat fee calculations...")
            mock_number_input.return_value = 5000

            try:
                # Test flat fee with different asset values
                test_cases = [
                    (1000000, 5000.0, "Basic flat fee failed"),
                    ('500,000', 5000.0, "Flat fee with formatted string failed"),
                    ('$1', 5000.0, "Flat fee with minimal assets failed"),
                    (0, 5000.0, "Flat fee with zero assets failed"),
                    (1000000000, 5000.0, "Flat fee with large assets failed")
                ]

                for assets, expected, message in test_cases:
                    print(f"Testing flat fee with assets: {assets}")
                    result = calculate_expected_fee(contract_flat, assets)
                    self.assertEqual(result, expected, message)

            except Exception as e:
                print("Error in flat fee calculations:")
                print(str(e))
                traceback.print_exc()
                raise

        # Test edge cases and invalid inputs
        print("\nTesting edge cases and invalid inputs...")
        try:
            test_cases = [
                (None, 1000000, None, "None contract failed"),
                (contract_percentage, None, None, "None assets failed"),
                (contract_percentage, 'invalid', None, "Invalid assets string failed"),
                (contract_percentage, 0, None, "Zero assets with percentage failed"),
                (contract_percentage, -1000, None, "Negative assets failed")
            ]

            for contract, assets, expected, message in test_cases:
                print(f"Testing edge case: contract={contract}, assets={assets}")
                result = calculate_expected_fee(contract, assets)
                self.assertEqual(result, expected, message)

        except Exception as e:
            print("Error in edge cases testing:")
            print(str(e))
            traceback.print_exc()
            raise

    except Exception as e:
        print("\nError in test_calculate_expected_fee:")
        print(str(e))
        traceback.print_exc()
        raise

if __name__ == '__main__':
    unittest.main()
