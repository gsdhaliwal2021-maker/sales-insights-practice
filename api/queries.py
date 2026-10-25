"""SQL behind each endpoint, kept apart from the web code.

Keeping SQL in plain strings here means you can paste any query straight into
a SQLite shell to check it, and the route functions stay short.

Both queries filter dates with a range (`>= start AND < end`) instead of
`strftime('%Y-%m', invoice_date) = :month`. A range can use the index on
invoice_date; wrapping the column in a function forces a full table scan.
"""

MONTHLY_REVENUE = """
SELECT
    strftime('%Y-%m', invoice_date) AS month,
    ROUND(SUM(revenue), 2)          AS revenue,
    COUNT(DISTINCT invoice_no)      AS orders,
    COUNT(DISTINCT customer_id)     AS customers
FROM transactions
GROUP BY month
ORDER BY month
"""

# A *repeat customer* in month M is someone who bought in M and has placed
# at least 2 orders (distinct invoices) in total by the end of M.
# That includes customers who came back from an earlier month AND customers
# who ordered twice within M. Two lines on one invoice are one order.
REPEAT_CUSTOMERS = """
WITH bounds AS (
    SELECT :month || '-01'                    AS start,
           date(:month || '-01', '+1 month')  AS stop
),
orders_to_date AS (           -- lifetime order count per customer up to end of M
    SELECT customer_id, COUNT(DISTINCT invoice_no) AS n_orders
    FROM transactions, bounds
    WHERE invoice_date < bounds.stop
    GROUP BY customer_id
),
active AS (                   -- customers who bought in M, with their M revenue
    SELECT customer_id, SUM(revenue) AS revenue
    FROM transactions, bounds
    WHERE invoice_date >= bounds.start AND invoice_date < bounds.stop
    GROUP BY customer_id
)
SELECT
    COUNT(*)                                                    AS active_customers,
    COALESCE(SUM(o.n_orders >= 2), 0)                           AS repeat_customers,
    ROUND(COALESCE(SUM(CASE WHEN o.n_orders >= 2 THEN a.revenue END), 0), 2)
                                                                AS repeat_revenue,
    ROUND(COALESCE(SUM(a.revenue), 0), 2)                       AS total_revenue
FROM active a
JOIN orders_to_date o USING (customer_id)
"""
