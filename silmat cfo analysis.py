import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# Connect to the Silmat Distributors database
conn = sqlite3.connect("silmat_distributors.db")

# Create table and insert expanded sample data covering multiple dates, statuses, and customers
conn.executescript("""
CREATE TABLE IF NOT EXISTS sales (
    order_id INTEGER PRIMARY KEY,
    date TEXT, 
    customer_name TEXT,
    product TEXT, 
    county TEXT,
    quantity INTEGER, 
    unit_price INTEGER,
    status TEXT
);

DELETE FROM sales;

INSERT INTO sales VALUES
(1, '2026-01-10', 'Kamau Stores', 'Maize Flour', 'Nairobi', 50, 3200, 'Completed'),
(2, '2026-01-15', 'Kamau Stores', 'Rice', 'Nairobi', 80, 2800, 'Completed'),
(3, '2026-01-20', 'Kamau Stores', 'Cooking Oil', 'Nairobi', 100, 4500, 'Completed'),
(4, '2026-01-12', 'Otieno Wholesale', 'Rice', 'Kisumu', 40, 4500, 'Completed'),
(5, '2026-02-05', 'Otieno Wholesale', 'Sugar', 'Kisumu', 60, 5500, 'Pending'),
(6, '2026-02-18', 'Otieno Wholesale', 'Cooking Oil', 'Kisumu', 90, 4500, 'Completed'),
(7, '2026-01-14', 'Coastal Supplies', 'Cooking Oil', 'Mombasa', 30, 4500, 'Cancelled'),
(8, '2026-02-10', 'Coastal Supplies', 'Wheat Flour', 'Mombasa', 50, 1800, 'Completed'),
(9, '2026-03-01', 'Coastal Supplies', 'Rice', 'Mombasa', 70, 2800, 'Completed'),
(10, '2026-01-15', 'Rift Valley Stores', 'Maize Flour', 'Nakuru', 40, 3200, 'Completed'),
(11, '2026-02-15', 'Rift Valley Stores', 'Sugar', 'Nakuru', 80, 5500, 'Completed'),
(12, '2026-03-10', 'Rift Valley Stores', 'Rice', 'Nakuru', 120, 2800, 'Completed');
""")
conn.commit()
print("Silmat Distributors Database Ready.\n")

# ==========================================
# CFO BOARD MEETING QUESTIONS (SQL + Pandas)
# ==========================================

# (1) Percentage of orders completed vs pending vs cancelled per county
q1 = """
SELECT county,
       ROUND(SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS completed_pct,
       ROUND(SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS pending_pct,
       ROUND(SUM(CASE WHEN status = 'Cancelled' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS cancelled_pct
FROM sales
GROUP BY county
"""
df_status = pd.read_sql_query(q1, conn)
# Business Interpretation: Mombasa exhibits a high fulfillment risk with 33% cancelled orders, whereas Nairobi maintains a flawless 100% completion rate.
print("--- (1) Order Status Percentage by County ---")
print(df_status.to_string(index=False), "\n")


# (2) Customers who increased order value consecutively using LAG
q2 = """
WITH order_values AS (
    SELECT customer_name, date, (quantity * unit_price) AS order_val
    FROM sales
),
lagged_orders AS (
    SELECT customer_name, date, order_val,
           LAG(order_val, 1) OVER (PARTITION BY customer_name ORDER BY date) AS prev_val,
           LAG(order_val, 2) OVER (PARTITION BY customer_name ORDER BY date) AS prev_prev_val
    FROM order_values
)
SELECT DISTINCT customer_name
FROM lagged_orders
WHERE order_val > prev_val AND prev_val > prev_prev_val;
"""
df_growth = pd.read_sql_query(q2, conn)
# Business Interpretation: Kamau Stores is our standout growth account, demonstrating consistent sequential order value expansion across three consecutive transactions.
print("--- (2) Consecutive Order Value Growth Customers ---")
print(df_growth.to_string(index=False), "\n")


# (3) Running total of revenue by date across all counties
q3 = """
WITH daily_revenue AS (
    SELECT date, SUM(quantity * unit_price) AS daily_rev
    FROM sales
    GROUP BY date
)
SELECT date, daily_rev,
       SUM(daily_rev) OVER (ORDER BY date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total_revenue
FROM daily_revenue
"""
df_running = pd.read_sql_query(q3, conn)
# Business Interpretation: Revenue accumulation shows a steady upward trajectory, crossing key valuation milestones driven by heavy bulk restocking phases in late February and March.
print("--- (3) Running Total Revenue by Date ---")
print(df_running.to_string(index=False), "\n")

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(df_running["date"], df_running["running_total_revenue"], marker='o', color="#1F4E79", linewidth=2.5)
ax.set_title("Silmat Distributors - Revenue Running Total Trend (KES)")
ax.set_xlabel("Date")
ax.set_ylabel("Cumulative Revenue (KES)")
ax.grid(True, linestyle="--", alpha=0.6)
plt.xticks(rotation=20)
plt.tight_layout()

plt.savefig("silmat_revenue_trend.png", dpi=150)
print("Trend chart successfully saved as: silmat_revenue_trend.png")

conn.close()
