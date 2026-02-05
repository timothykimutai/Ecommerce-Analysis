import logging
from pathlib import Path

import pandas as pd

DATA_PATH = Path("output/online_retail_cleaned.parquet")
RETURNS_PATH = Path("output/online_retail_returns.parquet")
SNAPSHOT_OFFSET_DAYS = 1

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def load_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Dataset missing at {path}")
    return pd.read_parquet(path)


def revenue_by_country(df: pd.DataFrame, top_n: int = 5):
    logger.info("\n--- Revenue by Country ---")
    
    country_revenue = df.groupby("Country", observed=True)["TotalRevenue"].sum().sort_values(ascending=False)
    total = country_revenue.sum()
    
    for country, revenue in country_revenue.head(top_n).items():
        share = (revenue / total) * 100
        logger.info(f"{country}: £{revenue:,.2f} ({share:.1f}%)")


def pareto_analysis(df: pd.DataFrame, threshold: float = 0.80):
    logger.info("\n--- Pareto Analysis (Products) ---")
    
    product_revenue = df.groupby("StockCode")["TotalRevenue"].sum().sort_values(ascending=False)
    total = product_revenue.sum()
    
    top_20_count = int(len(product_revenue) * 0.2)
    top_20_revenue = product_revenue.iloc[:top_20_count].sum()
    share = top_20_revenue / total
    
    logger.info(f"Top 20% Products ({top_20_count}): {share:.1%} of Total Revenue")
    
    if share >= threshold:
        logger.info("[Pass] Pareto principle holds.")
    else:
        logger.info(f"[Info] Revenue is more distributed (Share < {threshold:.0%}).")


def customer_retention(df: pd.DataFrame):
    logger.info("\n--- Customer Retention ---")
    
    invoice_counts = df.groupby("CustomerID")["InvoiceNo"].nunique()
    total = len(invoice_counts)
    one_time = (invoice_counts == 1).sum()
    repeat_rate = 1 - (one_time / total)
    
    logger.info(f"Total Customers: {total}")
    logger.info(f"Repeat Rate: {repeat_rate:.1%} ({total - one_time} customers)")


def build_rfm(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("\n--- RFM Segmentation ---")
    
    snapshot = df["InvoiceDate"].max() + pd.Timedelta(days=SNAPSHOT_OFFSET_DAYS)
    
    rfm = df.groupby("CustomerID").agg({
        "InvoiceDate": lambda x: (snapshot - x.max()).days,
        "InvoiceNo": "nunique",
        "TotalRevenue": "sum"
    })
    
    rfm.rename(columns={
        "InvoiceDate": "Recency",
        "InvoiceNo": "Frequency",
        "TotalRevenue": "Monetary"
    }, inplace=True)
    
    # quintile scoring
    rfm["R_Score"] = pd.qcut(rfm["Recency"], 5, labels=[5, 4, 3, 2, 1]).astype(int)
    
    rfm["F_Score"] = pd.cut(
        rfm["Frequency"].rank(pct=True), 
        bins=[0, 0.2, 0.4, 0.6, 0.8, 1.0], 
        labels=[1, 2, 3, 4, 5]
    ).astype(int)
    
    rfm["M_Score"] = pd.qcut(rfm["Monetary"], 5, labels=[1, 2, 3, 4, 5]).astype(int)
    
    def segment(row):
        if row["R_Score"] >= 5 and row["F_Score"] >= 4 and row["M_Score"] >= 4:
            return "Champion"
        if row["R_Score"] <= 2 and row["M_Score"] >= 4:
            return "At-Risk"
        if row["R_Score"] >= 4 and row["Frequency"] == 1:
            return "New Customer"
        return "Standard"
    
    rfm["Segment"] = rfm.apply(segment, axis=1)
    
    logger.info(f"Segment Distribution:\n{rfm['Segment'].value_counts().sort_index()}")
    logger.info(f"Segment Profiles (Mean):\n{rfm.groupby('Segment')[['Recency', 'Frequency', 'Monetary']].mean().round(1)}")
    
    return rfm


def basket_comparison(df: pd.DataFrame, rfm: pd.DataFrame):
    logger.info("\n--- Basket Analysis: At-Risk vs Champions ---")
    
    at_risk = rfm[rfm["Segment"] == "At-Risk"].index
    champions = rfm[rfm["Segment"] == "Champion"].index
    
    logger.info(f"At-Risk Customers: {len(at_risk)}")
    logger.info(f"Champion Customers: {len(champions)}")
    
    at_risk_txns = df[df["CustomerID"].isin(at_risk)]
    champion_txns = df[df["CustomerID"].isin(champions)]
    
    def top_products(txns, name, n=10):
        products = txns.groupby(["StockCode", "Description"])["TotalRevenue"].sum().sort_values(ascending=False)
        logger.info(f"\nTop {n} Products for {name}:")
        for (code, desc), rev in products.head(n).items():
            desc = desc if pd.notna(desc) else "N/A"
            logger.info(f"  {code} - {desc[:40]}: £{rev:,.2f}")
        return products
    
    at_risk_products = top_products(at_risk_txns, "At-Risk")
    champion_products = top_products(champion_txns, "Champions")
    
    logger.info("\n--- Basket Metrics Comparison ---")
    
    at_risk_size = at_risk_txns.groupby("InvoiceNo")["Quantity"].sum().mean()
    champion_size = champion_txns.groupby("InvoiceNo")["Quantity"].sum().mean()
    
    at_risk_value = at_risk_txns.groupby("InvoiceNo")["TotalRevenue"].sum().mean()
    champion_value = champion_txns.groupby("InvoiceNo")["TotalRevenue"].sum().mean()
    
    at_risk_unique = at_risk_txns["StockCode"].nunique()
    champion_unique = champion_txns["StockCode"].nunique()
    
    logger.info(f"Avg Basket Size (Items): At-Risk={at_risk_size:.1f}, Champions={champion_size:.1f}")
    logger.info(f"Avg Basket Value: At-Risk=£{at_risk_value:.2f}, Champions=£{champion_value:.2f}")
    logger.info(f"Unique Products: At-Risk={at_risk_unique}, Champions={champion_unique}")
    
    at_risk_codes = set(at_risk_products.index.get_level_values(0))
    champion_codes = set(champion_products.index.get_level_values(0))
    
    overlap = at_risk_codes & champion_codes
    at_risk_only = at_risk_codes - champion_codes
    
    logger.info(f"\n--- Product Overlap ---")
    logger.info(f"Common Products: {len(overlap)}")
    logger.info(f"At-Risk Only: {len(at_risk_only)}")
    logger.info(f"Champions Only: {len(champion_codes - at_risk_codes)}")
    
    if at_risk_only:
        logger.info(f"\nTop 5 Products Unique to At-Risk (Potential Issues):")
        unique_txns = at_risk_txns[at_risk_txns["StockCode"].isin(at_risk_only)]
        unique_rev = unique_txns.groupby(["StockCode", "Description"])["TotalRevenue"].sum().sort_values(ascending=False)
        for (code, desc), rev in unique_rev.head(5).items():
            desc = desc if pd.notna(desc) else "N/A"
            logger.info(f"  {code} - {desc[:40]}: £{rev:,.2f}")


def return_analysis(df: pd.DataFrame, rfm: pd.DataFrame):
    logger.info("\n--- Return Rate Analysis (Negative Friction) ---")
    
    if not RETURNS_PATH.exists():
        logger.warning(f"Returns data not found at {RETURNS_PATH}. Skipping.")
        return
    
    returns = pd.read_parquet(RETURNS_PATH)
    logger.info(f"Loaded {len(returns)} return records")
    
    returns = returns[returns["CustomerID"].notna()].copy()
    
    customer_returns = returns.groupby("CustomerID").agg({
        "InvoiceNo": "nunique",
        "Quantity": lambda x: abs(x).sum()
    }).rename(columns={"InvoiceNo": "ReturnCount", "Quantity": "ReturnedItems"})
    
    customer_sales = df.groupby("CustomerID").agg({
        "InvoiceNo": "nunique",
        "Quantity": "sum"
    }).rename(columns={"InvoiceNo": "OrderCount", "Quantity": "PurchasedItems"})
    
    metrics = customer_sales.join(customer_returns, how="left").fillna(0)
    metrics = metrics.join(rfm[["Segment"]], how="inner")
    
    metrics["ReturnRate"] = (metrics["ReturnCount"] / metrics["OrderCount"]) * 100
    metrics["ItemReturnRate"] = (metrics["ReturnedItems"] / metrics["PurchasedItems"]) * 100
    
    seg_returns = metrics.groupby("Segment").agg({
        "ReturnCount": "sum",
        "OrderCount": "sum",
        "ReturnedItems": "sum",
        "PurchasedItems": "sum",
        "ReturnRate": "mean",
        "ItemReturnRate": "mean"
    })
    
    seg_returns["OverallReturnRate"] = (seg_returns["ReturnCount"] / seg_returns["OrderCount"]) * 100
    seg_returns["OverallItemReturnRate"] = (seg_returns["ReturnedItems"] / seg_returns["PurchasedItems"]) * 100
    
    logger.info("\n--- Return Rates by Segment ---")
    for seg in ["Champion", "At-Risk", "New Customer", "Standard"]:
        if seg in seg_returns.index:
            row = seg_returns.loc[seg]
            logger.info(f"\n{seg}:")
            logger.info(f"  Order Return Rate: {row['OverallReturnRate']:.2f}% ({int(row['ReturnCount'])} returns / {int(row['OrderCount'])} orders)")
            logger.info(f"  Item Return Rate: {row['OverallItemReturnRate']:.2f}% ({int(row['ReturnedItems'])} items / {int(row['PurchasedItems'])} items)")
            logger.info(f"  Avg Customer Return Rate: {row['ReturnRate']:.2f}%")
    
    if "At-Risk" in seg_returns.index and "Champion" in seg_returns.index:
        logger.info("\n--- At-Risk vs Champions Comparison ---")
        at_risk_rate = seg_returns.loc["At-Risk", "OverallReturnRate"]
        champion_rate = seg_returns.loc["Champion", "OverallReturnRate"]
        
        diff = at_risk_rate - champion_rate
        logger.info(f"At-Risk Return Rate: {at_risk_rate:.2f}%")
        logger.info(f"Champion Return Rate: {champion_rate:.2f}%")
        logger.info(f"Difference: {diff:+.2f}% {'(Higher churn risk!)' if diff > 0 else '(Lower than Champions)'}")


def main():
    try:
        df = load_data(DATA_PATH)
        revenue_by_country(df)
        pareto_analysis(df)
        customer_retention(df)
        rfm = build_rfm(df)
        
        output = Path("output/rfm_table.parquet")
        rfm.to_parquet(output)
        logger.info(f"RFM Table saved to {output}")
        
        basket_comparison(df, rfm)
        return_analysis(df, rfm)
    except Exception as e:
        logger.critical(f"Analysis failed: {e}", exc_info=False)


if __name__ == "__main__":
    main()
