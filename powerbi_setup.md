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

## 🎨 Design System & Color Palette
Use these hex codes to ensure a professional, consistent "Modern Ecommerce" aesthetic.

### 1. Brand Colors
| Role | Color | Hex Code | Usage |
|------|-------|----------|-------|
| **Primary** | **Midnight Blue** | `#2C3E50` | Headers, KPI Cards, Main Titles |
| **Secondary** | **Ocean Teal** | `#1ABC9C` | Positive Trends, "Active Customer" Metrics |
| **Accent** | **Vibrant Coral** | `#FF6B6B` | Call-to-Actions, Highlighting Key Data |

### 2. Semantic Colors (Status Indicators)
| Role | Color | Hex Code | Usage |
|------|-------|----------|-------|
| **Success / Good** | **Emerald Green** | `#2ECC71` | Growth, Profit, "Champions" Segment |
| **Warning / Risk** | **Amber Orange** | `#F39C12` | "At-Risk" Segment, Slowing Trends |
| **Danger / Bad** | **Alizarin Red** | `#E74C3C` | Churn, Returns, Negative Growth |
| **Neutral** | **Slate Grey** | `#95A5A6` | Contextual text, Axis labels, Comparison lines |

### 3. Typography Guidelines
* **Font Family**: standard sans-serif (e.g., DIN, Segoe UI).
* **Size Hierarchy**:
    * **KPI Values**: 45pt (Bold)
    * **KPI Labels**: 12pt (Regular, Grey)
    * **Chart Titles**: 14pt (Semi-Bold)

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
   - **Revenue** (was Total Revenue): Total sales volume. *Goal: Growth.*
   - **Customers** (was Active Customer Base): Unique active buyers. *Goal: Reach.*
   - **AOV** (was Avg Order Value): Average spend per order. *Goal: Efficiency.*
   - **Risk** (was Attrition Risk): % of customers in "At-Risk" segment. *Goal: Minimization.*

**2. Revenue Trend (Line Chart)**
   - **Title**: "Revenue Performance Over Time"
   - **X-Axis**: `Calendar[Date]` (Use the Date Hierarchy: Year > Month)
   - **Y-Axis**: `Total Revenue`
   - **Add-on**: Add a **Trend Line** from the Analytics pane to show trajectory.

**3. Revenue Share (Donut Chart)**
   - **Title**: "Revenue Mix by Segment"
   - **Legend**: `Customers[Segment]`
   - **Values**: `Total Revenue`
   - *Insight: Visualizes the reliance on "Champions" vs "At-Risk".*

**4. Market Performance (Table)**
   - **Title**: "Top Markets Breakdown"
   - **Columns**:
     - `Sales[Country]`
     - `Total Revenue` (Data Bar conditional formatting)
     - `Total Orders`
     - `Avg Order Value (AOV)`
   - *Insight: detailed look at where the money is coming from.*
