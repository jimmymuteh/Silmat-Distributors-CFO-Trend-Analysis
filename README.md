# Silmat Distributors — CFO Trend Analysis
A Python script I put together to help the CFO and board track operational trends, spot fulfillment risks, and analyze revenue growth over time using advanced SQL (including window functions and `LAG`).
## Key Takeaways from the Data
* **Fulfillment Risks:** Mombasa is showing a 33% cancellation rate, while Nairobi is sitting at a clean 100% completion rate.
* **Top Growth Account:** Kamau Stores is our standout customer, showing consistent order growth across consecutive transactions.
* **Revenue Velocity:** Cumulative revenue shows strong upward momentum, driven by heavy bulk restocking cycles in February and March.
## What the Script Does
1. Sets up the SQLite database with expanded customer and order records.
2. Runs advanced SQL queries to calculate status percentages, track order value growth with `LAG`, and compute running totals.
3. Automatically generates and saves a clean cumulative revenue trend chart (`silmat_revenue_trend.png`).