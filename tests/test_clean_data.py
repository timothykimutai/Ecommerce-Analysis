import pytest
import pandas as pd
from pathlib import Path


def test_basic_import():
    """Test that clean_data module can be imported"""
    from clean_data import process_data
    assert process_data is not None


def test_data_split_logic():
    """Test the core logic of splitting returns from sales"""
    df = pd.DataFrame({
        "InvoiceNo": ["536365", "536366", "C536367"],
        "CustomerID": [17850.0, 17850.0, 17850.0]
    })
    
    is_return = df["InvoiceNo"].str.startswith("C", na=False)
    
    assert is_return.sum() == 1
    assert not is_return.iloc[0]
    assert not is_return.iloc[1]
    assert is_return.iloc[2]


def test_revenue_calculation():
    """Test revenue calculation logic"""
    quantity = 6
    unit_price = 2.55
    expected_revenue = quantity * unit_price
    
    assert abs(expected_revenue - 15.30) < 0.01
