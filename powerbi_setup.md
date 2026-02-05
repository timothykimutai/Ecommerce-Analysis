# Power BI Setup Guide

## 📊 Business Glossary & Logic
Before setting up the dashboard, align on these business definitions to ensure stakeholder clarity:

| Technical Term | Business Term | Definition |
|----------------|---------------|------------|
| `Recency` | **Days Since Last Purchase** | Number of days since the customer's most recent transaction. |
| `Frequency` | **Lifetime Orders** | Total count of unique orders placed by the customer. |
| `Monetary` | **Lifetime Revenue** | Total value of all purchases made by the customer (£). |
| `Churn Rate` | **Customer Attrition Risk** | Percentage of high-value customers showing signs of inactivity. |
| `InvoiceNo` | **Order ID** | Unique identifier for a single transaction. |

---

## Data Sources (Remote Access)
Connect directly to these GitHub raw files using the **Web** connector in Power BI.

**1. Sales Transactions (Fact)**
   - **Business Use**: analyzing revenue, volume, and product performance.
   - URL: `https://github.com/timothykimutai/Ecommerce-Analysis/raw/main/output/online_retail_cleaned.parquet`

**2. Customer Segments (Dimension)**
   - **Business Use**: Filtering by customer value tiers (Champions vs. At-Risk).
   - URL: `https://github.com/timothykimutai/Ecommerce-Analysis/raw/main/output/rfm_table.parquet`

**3. Returns Data (Fact)**
   - **Business Use**: Tracking product quality issues and negative friction.
   - URL: `https://github.com/timothykimutai/Ecommerce-Analysis/raw/main/output/online_retail_returns.parquet`

**4. Calendar (Dimension)**
   - **Business Use**: Time-intelligence analysis (MoM, YoY).
   - URL: `https://github.com/timothykimutai/Ecommerce-Analysis/raw/main/output/date_dimension.parquet`

---

## Data Model Setup

1. **Load Data**: Use the **Web** connector for the URLs above.
2. **Rename Tables** (Optional but Recommended):
   - `online_retail_cleaned` -> **Sales**
   - `rfm_table` -> **Customers**
   - `online_retail_returns` -> **Returns**
   - `date_dimension` -> **Calendar**
3. **Relationships**:
   - Link **Sales[CustomerID]** to **Customers[CustomerID]** (Many-to-One).
   - Link **Returns[CustomerID]** to **Customers[CustomerID]** (Many-to-One).
   - Link **Sales[InvoiceDate]** to **Calendar[Date]** (Many-to-One).

---

## Page 1: The Executive Pulse (Implementation)

### Required Measures (DAX)
*Use these business-friendly names for your measures:*

**A. Core Business KPIs**
```dax
Total Revenue = SUM(Sales[TotalRevenue])
Total Orders = DISTINCTCOUNT(Sales[InvoiceNo])
Active Customer Base = DISTINCTCOUNT(Sales[CustomerID])
Avg Order Value (AOV) = DIVIDE([Total Revenue], [Total Orders])
```

**B. Risk & Retention Metrics**
```dax
High Risk Customers = CALCULATE(COUNT(Customers[CustomerID]), Customers[Segment] = "At-Risk")
Attrition Risk % = DIVIDE([High Risk Customers], COUNTROWS(Customers))
Product Return Rate = DIVIDE(COUNT(Returns[InvoiceNo]), [Total Orders])
```

**C. Growth Indicators (MoM)**
```dax
Revenue Last Month = CALCULATE([Total Revenue], DATEADD('Calendar'[Date], -1, MONTH))
Monthly Growth % = IF([Revenue Last Month] = 0, BLANK(), DIVIDE([Total Revenue] - [Revenue Last Month], [Revenue Last Month]))
```

---

### Visuals Configuration

**1. The "North Star" Cards (Top Row)**
   - **Revenue Health**: `Total Revenue` (with `Monthly Growth %` as callout).
   - **Customer Base**: `Active Customer Base`.
   - **Order Value**: `Avg Order Value (AOV)`.
   - **Retention Warning**: `Attrition Risk %` (Color red if > 20%).

**2. Revenue Trend (Line Chart)**
   - **Title**: "Revenue Performance Year-to-Date"
   - **X-Axis**: `Calendar[MonthName]`
   - **Y-Axis**: `Total Revenue`
   - **Add-on**: Add a **Trend Line** from the Analytics pane to show trajectory.

**3. Global Performance (Map)**
   - **Title**: "Revenue by Market"
   - **Location**: `Sales[Country]`
   - **Bubble Size**: `Total Revenue`

**4. Portfolio Health (Treemap)**
   - **Title**: "Revenue Contribution by Segment"
   - **Category**: `Customers[Segment]`
   - **Values**: `Total Revenue`
   - *Insight: Quickly see if "Champions" are driving the majority of revenue.*
