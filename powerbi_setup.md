# Power BI Setup Guide

## Data Sources (Remote Access)
You can connect Power BI directly to the raw files on GitHub. This allows you to build reports without keeping the files local.

**1. `online_retail_cleaned.parquet` (Sales Fact)**
   - URL: `https://github.com/timothykimutai/Ecommerce-Analysis/raw/main/output/online_retail_cleaned.parquet`

**2. `rfm_table.parquet` (Dimension)**
   - URL: `https://github.com/timothykimutai/Ecommerce-Analysis/raw/main/output/rfm_table.parquet`

**3. `online_retail_returns.parquet` (Returns Fact)**
   - URL: `https://github.com/timothykimutai/Ecommerce-Analysis/raw/main/output/online_retail_returns.parquet`

**4. `date_dimension.parquet` (Date Dimension)**
   - URL: `https://github.com/timothykimutai/Ecommerce-Analysis/raw/main/output/date_dimension.parquet`

## Data Model Setup

1. **Get Data**:
   - Select **Web** connector.
   - Excel/CSV/Parquet connectors usually require a local path. For remote parquet, use **Web** and paste the URLs above.
   - *Note: If Power BI doesn't natively support "Parquet from Web" easily, you might need a small Power Query script or download them locally.*

   **Power Query Script (M) for Web Parquet**:
   ```powerquery
   let
       Source = Parquet.Document(Web.Contents("https://github.com/timothykimutai/Ecommerce-Analysis/raw/main/output/rfm_table.parquet"))
   in
       Source
   ```

2. **Relationships**:
   - Create a relationship between `online_retail_cleaned` and `rfm_table` using **`CustomerID`**.
   - Cardinality: **Many-to-One** (* (Sales) -> 1 (Customers)).
   - Cross-filter direction: **Single**.

3. **Measures to Create**:
   - `Total Revenue = SUM(online_retail_cleaned[TotalRevenue])`
   - `Active Customers = DISTINCTCOUNT(online_retail_cleaned[CustomerID])`
   - `Avg Order Value = AVERAGE(online_retail_cleaned[TotalRevenue])`
   - `Return Rate = DIVIDE(COUNT(online_retail_returns[InvoiceNo]), COUNT(online_retail_cleaned[InvoiceNo]))`

## Page 1: The Executive Pulse (Implementation)

### 1. Data Prep (New)
I have generated a `date_dimension.parquet` file for you. Import this and link `Date` column to `online_retail_cleaned[InvoiceDate]`. This allows for accurate "Prior Period" calculations.

### 2. Required Measures (DAX)
Create a new measure table or add these to your Sales table:

**A. Core KPIs**
```dax
Total Revenue = SUM(online_retail_cleaned[TotalRevenue])
Total Customers = DISTINCTCOUNT(online_retail_cleaned[CustomerID])
AOV = DIVIDE([Total Revenue], COUNT(online_retail_cleaned[InvoiceNo]))
churn_risk_count = CALCULATE(COUNT(rfm_table[CustomerID]), rfm_table[Segment] = "At-Risk")
Churn Rate % = DIVIDE([churn_risk_count], COUNTROWS(rfm_table))
```

**B. Time Intelligence (Revenue vs Prior Period)**
```dax
Revenue PM = CALCULATE([Total Revenue], DATEADD('date_dimension'[Date], -1, MONTH))
Revenue Trend = IF([Revenue PM] = 0, BLANK(), DIVIDE([Total Revenue] - [Revenue PM], [Revenue PM]))
```

### 3. Visuals Configuration

**KPI Cards**
- Card 1: `Total Revenue` (Callout value), `Revenue Trend` (Trend axis or subtitle)
- Card 2: `Total Customers`
- Card 3: `AOV`
- Card 4: `Churn Rate %` (Format as percentage, maybe turn red if > 20%)

**Trend Chart (Line Chart)**
- **X-Axis**: `date_dimension[MonthName]` (Sort by Month Number)
- **Y-Axis**: `Total Revenue`
- **Analytics Pane**: Add a "Trend Line"

**Geographic Pulse (Map)**
- **Location**: `online_retail_cleaned[Country]`
- **Bubble Size**: `Total Revenue`

**Segment Breakdown (Treemap)**
- **Category**: `rfm_table[Segment]`
- **Values**: `Total Revenue` (to show value ownership) or `Total Customers` (to show population size)

## Visualization Ideas
- **Segment Overview**: Bar chart of `Total Revenue` by `Segment`.
- **Churn Risk**: Pie chart of customer counts by `Segment`.
- **Geographic Impact**: Map using `Country` and `Total Revenue`.
