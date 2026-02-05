import logging
from pathlib import Path
from typing import Tuple

import pandas as pd
import pandera as pa
from pandera import Column, DataFrameSchema, Check

INPUT_FILE = Path("Online Retail.xlsx")
OUTPUT_DIR = Path("output")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

SCHEMA = DataFrameSchema({
    "InvoiceNo": Column(str),
    "StockCode": Column(str),
    "Description": Column(str, nullable=True),
    "Quantity": Column(int, Check.gt(0)),
    "InvoiceDate": Column(pa.DateTime),
    "UnitPrice": Column(float, Check.gt(0)),
    "CustomerID": Column(float),
    "Country": Column(str),
    "TotalRevenue": Column(float, Check.ge(0)),
}, strict=False)


def process_data(path: Path) -> Tuple[pd.DataFrame, pd.DataFrame]:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    logger.info(f"Ingesting {path}...")
    df = pd.read_excel(path)

    df.dropna(subset=["CustomerID"], inplace=True)
    
    df["InvoiceNo"] = df["InvoiceNo"].astype(str)
    df["StockCode"] = df["StockCode"].astype(str)
    # Ensure InvoiceDate is normalized to midnight (Date only) for Power BI relationships
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce").dt.normalize()
    df["Country"] = df["Country"].astype("category")

    is_return = df["InvoiceNo"].str.startswith("C", na=False)
    
    returns = df[is_return].copy()
    sales = df[~is_return].copy()
    
    sales = sales[(sales["Quantity"] > 0) & (sales["UnitPrice"] > 0)]
    sales["TotalRevenue"] = sales["Quantity"] * sales["UnitPrice"]

    try:
        sales = SCHEMA.validate(sales, lazy=True)
    except pa.errors.SchemaErrors as e:
        logger.error(f"Schema validation errors: {e.failure_cases}")
        raise

    logger.info(f"Processed {len(sales)} sales, {len(returns)} returns")
    logger.info(f"Processed {len(sales)} sales, {len(returns)} returns")
    return sales, returns


def create_date_dimension(start_date: pd.Timestamp, end_date: pd.Timestamp) -> pd.DataFrame:
    """Create a calendar dimension table for time-series analysis"""
    dates = pd.date_range(start=start_date, end=end_date, freq="D")
    date_df = pd.DataFrame({"Date": dates})
    
    date_df["Year"] = date_df["Date"].dt.year
    date_df["Quarter"] = date_df["Date"].dt.quarter
    date_df["Month"] = date_df["Date"].dt.month
    date_df["MonthName"] = date_df["Date"].dt.month_name()
    date_df["Week"] = date_df["Date"].dt.isocalendar().week.astype(int)
    date_df["DayOfWeek"] = date_df["Date"].dt.dayofweek
    date_df["DayName"] = date_df["Date"].dt.day_name()
    
    return date_df


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    try:
        sales, returns = process_data(INPUT_FILE)
        
        sales.to_parquet(OUTPUT_DIR / "online_retail_cleaned.parquet", compression="snappy", index=False)
        returns.to_parquet(OUTPUT_DIR / "online_retail_returns.parquet", compression="snappy", index=False)
        
        # Create and save Date Dimension
        min_date = sales["InvoiceDate"].min()
        max_date = sales["InvoiceDate"].max()
        date_dim = create_date_dimension(min_date, max_date)
        date_dim.to_parquet(OUTPUT_DIR / "date_dimension.parquet", compression="snappy", index=False)

        
        logger.info(f"Data saved to {OUTPUT_DIR}")
        
    except Exception as e:
        logger.critical("ETL failed", exc_info=True)
        raise


if __name__ == "__main__":
    main()
