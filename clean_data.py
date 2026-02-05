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
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")
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
    return sales, returns


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    try:
        sales, returns = process_data(INPUT_FILE)
        
        sales.to_parquet(OUTPUT_DIR / "online_retail_cleaned.parquet", compression="snappy", index=False)
        returns.to_parquet(OUTPUT_DIR / "online_retail_returns.parquet", compression="snappy", index=False)
        
        logger.info(f"Data saved to {OUTPUT_DIR}")
        
    except Exception as e:
        logger.critical("ETL failed", exc_info=True)
        raise


if __name__ == "__main__":
    main()
