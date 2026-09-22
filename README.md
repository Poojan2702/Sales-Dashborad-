# Sales Data Analyst Project — Python + Excel

## Project overview
This is a complete beginner-to-intermediate **Data Analyst portfolio project** built around the supplied structured Excel sales dataset.

The project uses:
- **Excel** as the only data source
- **Python + Pandas** for data loading, cleaning, transformation and KPI calculations
- **Plotly** for interactive charts
- **Streamlit** for the frontend dashboard
- A single Python file for the application/backend logic

No SQL database or external API is required.

## Files
```text
sales_dashboard.py   # Single-file Python application: backend + Streamlit frontend
requirements.txt     # Python dependencies
README.md            # Project documentation
Project_Summary.docx # Portfolio/project summary
```

## Dataset
Expected Excel filename:
```text
sales data .xlsx
```

The supplied workbook contains 18,045 transaction records and 36 columns, including:
- Transaction / order / customer identifiers
- Customer demographics and segments
- Order date and time
- Sales channel
- Store, country, region and city
- Product/category information
- Quantity, price, discount, sales, cost and profit
- Payment and order status
- Shipping and delivery data
- Returns
- Sales representative / promotion information
- Customer rating and inventory level
- Order year

## Dashboard features
### KPI layer
- Total Sales
- Total Profit
- Orders
- Units Sold
- Profit Margin
- Return Rate

### Interactive analysis
- Sales & profit monthly trend
- Sales by product category
- Sales by country
- Sales channel mix
- Top 10 products by sales
- Return analysis
- Data-quality snapshot
- Filtered-data preview
- Filtered CSV download

### Filters
- Product Category
- Sales Channel
- Country
- Customer Segment
- Order Date Range

## How to run

### 1. Install Python
Python 3.10+ is recommended.

### 2. Put these files in the same folder
```text
sales_dashboard.py
requirements.txt
sales data .xlsx
```

### 3. Install dependencies
Windows:
```bash
python -m pip install -r requirements.txt
```

macOS/Linux:
```bash
python3 -m pip install -r requirements.txt
```

### 4. Start the dashboard
```bash
streamlit run sales_dashboard.py
```

The browser should open the dashboard automatically.

## Optional Excel upload
The dashboard also has an **Upload Excel file** control in the sidebar. This lets you analyze another workbook with the same/compatible column structure without changing the Python code.

## Portfolio talking points
You can describe the project as:

> "Built an interactive sales analytics dashboard using Python, Pandas, Plotly and Streamlit. Loaded and standardized structured Excel transaction data, created business KPIs and derived metrics, implemented dynamic filters, analyzed sales/profit trends, product performance, geography, sales channels and returns, and added downloadable filtered data."

## Important implementation note
The app normalizes common text inconsistencies such as different capitalization in product categories, order status and payment method. It does not overwrite the original Excel workbook.

## Troubleshooting
**Excel file not found**
- Keep `sales data .xlsx` in the same folder as `sales_dashboard.py`, or
- Upload the workbook through the sidebar.

**Module not found**
```bash
python -m pip install -r requirements.txt
```

**Streamlit command not found**
```bash
python -m streamlit run sales_dashboard.py
```
