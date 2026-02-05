import pytest
import pandas as pd
from pathlib import Path


@pytest.fixture
def sample_sales():
    """Sample sales data for testing - needs enough rows for quintile scoring"""
    dates = pd.date_range("2010-12-01", periods=25, freq="D")
    return pd.DataFrame({
        "CustomerID": [17850.0] * 10 + [13047.0] * 8 + [12583.0] * 4 + [15311.0] * 3,
        "InvoiceNo": [f"53636{i}" for i in range(25)],
        "InvoiceDate": dates,
        "TotalRevenue": [100.0, 150.0, 200.0, 50.0, 75.0] * 5,
        "StockCode": [f"STOCK{i%10}" for i in range(25)],
        "Quantity": [10, 15, 20, 5, 7] * 5,
        "Country": ["UK"] * 15 + ["France"] * 7 + ["Germany"] * 3
    })


def test_build_rfm_creates_correct_columns(sample_sales):
    """Test that RFM table has required columns"""
    from analysis import build_rfm
    
    rfm = build_rfm(sample_sales)
    
    required_cols = ["Recency", "Frequency", "Monetary", "R_Score", "F_Score", "M_Score", "Segment"]
    for col in required_cols:
        assert col in rfm.columns


def test_build_rfm_calculates_frequency(sample_sales):
    """Test that frequency is calculated correctly"""
    from analysis import build_rfm
    
    rfm = build_rfm(sample_sales)
    
    # Customer 17850 has 10 orders
    assert rfm.loc[17850.0, "Frequency"] == 10
    # Customer 13047 has 8 orders
    assert rfm.loc[13047.0, "Frequency"] == 8


def test_build_rfm_calculates_monetary(sample_sales):
    """Test that monetary value is calculated correctly"""
    from analysis import build_rfm
    
    rfm = build_rfm(sample_sales)
    
    # Customer 17850: 100+150+200+50+75+100+150+200+50+75 = 1150
    assert rfm.loc[17850.0, "Monetary"] == 1150.0


def test_build_rfm_assigns_segments(sample_sales):
    """Test that segments are assigned"""
    from analysis import build_rfm
    
    rfm = build_rfm(sample_sales)
    
    assert "Segment" in rfm.columns
    assert rfm["Segment"].notna().all()
    assert set(rfm["Segment"].unique()).issubset({"Champion", "At-Risk", "New Customer", "Standard"})


def test_revenue_by_country(sample_sales):
    """Test revenue by country runs without error"""
    from analysis import revenue_by_country
    
    # Should not raise an exception
    revenue_by_country(sample_sales, top_n=2)


def test_pareto_analysis(sample_sales):
    """Test Pareto analysis runs without error"""
    from analysis import pareto_analysis
    
    # Should not raise an exception
    pareto_analysis(sample_sales)
