# tests/test_unit_main.py
import pytest
from main import clean_price

@pytest.mark.parametrize("input_price, expected_output", [
    ("1,234.56", 1234.56),
    ("1.234,56", 1234.56),
    (" $1,234.56 ", 1234.56),
    ("1,234", 1234.0),
    ("1234.56", 1234.56),
    ("1234", 1234.0),
    (None, None),
    ("Error", None),
    ("abc", None),
    ("", None)
])
def test_clean_price(input_price, expected_output):
    """Test the clean_price function with various formats."""
    assert clean_price(input_price) == expected_output
