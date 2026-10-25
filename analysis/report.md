# Why repeat-customer revenue fell from Q2 to Q3 2026

**Repeat-customer revenue fell 40%, from $52,392 in Q2 (Apr–Jun) to $31,423 in Q3 (Jul–Sep), a drop of $20,970.**

Prices did not change on any product, so the whole decline is customers buying fewer items. Three reasons account for it:

| # | Reason | Dimension | Impact |
|---|---|---|---|
| 1 | **Established customers ordered less often.** Retained repeat customers went from 2.96 to 2.18 orders a quarter, with smaller orders ($73 → $57). The April cohort alone accounts for 82% of the drop. | Cohort | −$17,263 from the April cohort |
| 2 | **Germany's order sizes collapsed in July.** Units per line fell from 8.0 to 2.4 while the number of German customers held steady. Germany is 16% of Q2 repeat revenue but 31% of the decline. | Country | −$6,396 (−78%) |
| 3 | **Three products fell off a cliff in July:** White Metal Lantern, Natural Slate Heart Chalkboard and Cream Cupid Hearts Coat Hanger. Units dropped 64–69%, against about 29% for the other twelve products outside Germany. | Product | −$7,132 (34% of the decline) |

Reason 1 is the broad baseline: every country and product lost revenue, most of them between 20% and 55%. Reasons 2 and 3 are concentrated, sudden drops *on top of* that baseline, and both start sharply in July, which points to specific events worth investigating rather than general softness. The reasons overlap (German purchases of the three products count in both #2 and #3, and the April cohort spans everything), so their impacts don't add to 100%. Removing the $1,262 overlap, #2 and #3 together explain $12,266, or 58% of the decline.

---

## Definitions

- **Quarters:** Q2 = 1 Apr–30 Jun 2026, Q3 = 1 Jul–30 Sep 2026. These are the only two full quarters in the data.
- **Repeat customer:** bought in the quarter **and** has 2+ orders (distinct invoices) in total by the quarter's end. This matches `GET /metrics/repeat-customers`, so the API and this report agree.
- **Repeat-customer revenue:** revenue in the quarter from repeat customers.
- **Cohort:** the month of a customer's first purchase in the data.
- **Data:** the cleaned `transactions` table from `python -m pipeline` (cancellations, missing customer IDs, zero-price lines and duplicates removed).

## How the decline breaks down

### Who moved: the customer bridge

Every customer who was a repeat customer in either quarter falls into one bucket:

| Status | Customers | Q2 | Q3 | Change |
|---|---:|---:|---:|---:|
| Retained (repeat in both quarters) | 204 | $44,186 | $25,216 | **−$18,969** |
| Lapsed (repeat in Q2, didn't buy in Q3) | 34 | $8,207 | $0 | −$8,207 |
| New repeat (Q2 one-timers who came back in Q3) | 51 | $0 | $6,206 | +$6,206 |

The biggest piece is the same customers spending less (−$19.0k), not customers leaving (−$8.2k). Returning one-time buyers partly offset the losses.

Related: **every Q3 customer had also bought in Q2.** No new customers arrived in Q3. That doesn't change repeat revenue this quarter, but it means there is no pipeline of future repeat customers.

### Reason 1: Cohort

| Cohort | Repeat cust. Q2 | Repeat cust. Q3 | Q2 | Q3 | Change | Change % | Share of Q2 base | Share of decline |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2026-04 | 162 | 157 | $36,411 | $19,148 | −$17,263 | −47.4% | 69.5% | **82.3%** |
| 2026-05 | 61 | 62 | $13,433 | $8,138 | −$5,296 | −39.4% | 25.6% | 25.3% |
| 2026-06 | 15 | 36 | $2,548 | $4,137 | +$1,589 | +62.4% | 4.9% | −7.6% |

The April cohort is the largest and also fell the fastest. The June cohort grew because many of its one-time buyers came back and became repeat customers in Q3.

Why did retained customers spend less? Both fewer orders and smaller orders:

| Cohort | Orders/customer Q2 | Orders/customer Q3 | Avg order Q2 | Avg order Q3 | Retained customers |
|---|---:|---:|---:|---:|---:|
| 2026-04 | 3.07 | 2.21 | $72.66 | $55.78 | 141 |
| 2026-05 | 2.88 | 2.27 | $73.68 | $60.17 | 49 |
| 2026-06 | 2.14 | 1.57 | $77.83 | $54.05 | 14 |
| **All** | **2.96** | **2.18** | **$73.15** | **$56.79** | **204** |

Order frequency fell 26% and order value fell 22%, in every country. This baseline decline could be seasonal (a spring/early-summer peak) but six months of data can't tell seasonality apart from a real slowdown.

### Reason 2: Country

| Country | Q2 | Q3 | Change | Change % | Share of Q2 base | Share of decline | Customers Q2 → Q3 | Orders/cust. Q2 → Q3 | Units/line Q2 → Q3 |
|---|---:|---:|---:|---:|---:|---:|---|---|---|
| United Kingdom | $23,847 | $16,573 | −$7,274 | −30.5% | 45.5% | 34.7% | 114 → 120 | 2.95 → 2.29 | 7.58 → 6.67 |
| **Germany** | $8,172 | $1,775 | **−$6,396** | **−78.3%** | 15.6% | **30.5%** | 34 → 36 | 3.18 → 2.14 | **8.03 → 2.35** |
| Spain | $4,593 | $2,159 | −$2,434 | −53.0% | 8.8% | 11.6% | 18 → 17 | 3.17 → 2.00 | 7.57 → 6.79 |
| Ireland | $3,740 | $1,694 | −$2,045 | −54.7% | 7.1% | 9.8% | 19 → 15 | 2.95 → 2.00 | 7.73 → 6.16 |
| France | $7,391 | $5,468 | −$1,923 | −26.0% | 14.1% | 9.2% | 33 → 41 | 3.06 → 2.20 | 8.40 → 6.31 |
| Netherlands | $4,650 | $3,753 | −$897 | −19.3% | 8.9% | 4.3% | 20 → 26 | 2.80 → 2.08 | 8.06 → 6.91 |

The UK lost the most dollars, but in line with its size. Germany is the outlier: its customers kept ordering at roughly the same frequency as everyone else, but each line shrank from about 8 units to about 2. 14 of the 15 products fell 66–88% in Germany (the exception, Party Bunting, fell 24%), so this is not about one product.

It's a step change, not a slide:

| Month | Germany units/line | Other countries units/line |
|---|---:|---:|
| 2026-04 | 7.79 | 7.53 |
| 2026-05 | 8.32 | 8.02 |
| 2026-06 | 7.97 | 7.69 |
| 2026-07 | **2.10** | 6.62 |
| 2026-08 | 2.59 | 6.57 |
| 2026-09 | 2.47 | 6.62 |

**Worth checking:** a change around 1 July affecting German orders, such as shipping costs or a minimum-order threshold, a pack-size or unit-of-measure change in how German orders are recorded, or a large German reseller switching supplier.

### Reason 3: Product

| Product | Q2 | Q3 | Change | Share of decline | Units Q2 → Q3 | Units change | Price Q2 → Q3 |
|---|---:|---:|---:|---:|---|---:|---|
| REGENCY CAKESTAND 3 TIER | $12,814 | $9,996 | −$2,818 | 13.4% | 1,005 → 784 | −22.0% | $12.75 → $12.75 |
| **WHITE METAL LANTERN** | $3,905 | $1,278 | −$2,627 | 12.5% | 1,152 → 377 | **−67.3%** | $3.39 → $3.39 |
| **NATURAL SLATE HEART CHALKBOARD** | $3,419 | $1,056 | −$2,363 | 11.3% | 1,159 → 358 | **−69.1%** | $2.95 → $2.95 |
| PARTY BUNTING | $5,103 | $2,935 | −$2,168 | 10.3% | 1,031 → 593 | −42.5% | $4.95 → $4.95 |
| **CREAM CUPID HEARTS COAT HANGER** | $3,347 | $1,205 | −$2,142 | 10.2% | 1,217 → 438 | **−64.0%** | $2.75 → $2.75 |
| PAPER CHAIN KIT 50'S CHRISTMAS | $3,794 | $1,832 | −$1,962 | 9.4% | 1,286 → 621 | −51.7% | $2.95 → $2.95 |
| SET OF 3 CAKE TINS PANTRY DESIGN | $5,386 | $3,965 | −$1,421 | 6.8% | 1,088 → 801 | −26.4% | $4.95 → $4.95 |
| WHITE HANGING HEART T-LIGHT HOLDER | $2,468 | $1,183 | −$1,285 | 6.1% | 968 → 464 | −52.1% | $2.55 → $2.55 |
| RABBIT NIGHT LIGHT | $2,729 | $1,756 | −$973 | 4.6% | 1,312 → 844 | −35.7% | $2.08 → $2.08 |
| LUNCH BAG RED RETROSPOT | $2,091 | $1,304 | −$787 | 3.8% | 1,267 → 790 | −37.6% | $1.65 → $1.65 |
| ASSORTED COLOUR BIRD ORNAMENT | $1,796 | $1,031 | −$766 | 3.7% | 1,063 → 610 | −42.6% | $1.69 → $1.69 |
| JUMBO BAG RED RETROSPOT | $2,600 | $1,972 | −$628 | 3.0% | 1,250 → 948 | −24.2% | $2.08 → $2.08 |
| STRAWBERRY CERAMIC TRINKET BOX | $1,258 | $828 | −$430 | 2.1% | 1,006 → 662 | −34.2% | $1.25 → $1.25 |
| POPCORN HOLDER | $1,020 | $691 | −$329 | 1.6% | 1,200 → 813 | −32.3% | $0.85 → $0.85 |
| PACK OF 72 RETROSPOT CAKE CASES | $663 | $392 | −$271 | 1.3% | 1,205 → 713 | −40.8% | $0.55 → $0.55 |

The Regency Cakestand lost the most dollars, but only because it's the most expensive item; its units fell 22%, *less* than average. Ranked by how much volume fell, three products stand apart, and the gap holds with Germany removed (−64% vs −29%). Like Germany, it happened at once in July:

| Month | Units of the 3 products | Units of the other 12 |
|---|---:|---:|
| 2026-04 | 933 | 4,158 |
| 2026-05 | 1,360 | 5,284 |
| 2026-06 | 1,235 | 4,239 |
| 2026-07 | **384** | 2,964 |
| 2026-08 | 429 | 2,884 |
| 2026-09 | 360 | 2,795 |

**Worth checking:** stock-outs, delisting or a listing change for these three items from July. These are all home-decor items, so a seasonal or range change is also plausible.

## Does the story depend on the definition?

A definition can create a trend that isn't real, so I re-ran the key comparisons with a stricter rule: a repeat customer needs **2+ orders within the quarter** (no credit for Q2 history in Q3).

| Check | Main definition | Strict definition |
|---|---:|---:|
| Total repeat revenue change | −40.0% | −50.5% |
| Germany revenue change | −78.3% | −80.5% |
| Other countries revenue change | −33.0% | −44.9% |
| 3 products, units change (ex-Germany) | −63.9% | −69.7% |
| Other 12 products, units change (ex-Germany) | −29.3% | −42.0% |

The size of the decline depends on the definition, but all three reasons hold under both: Germany and the three products drop far more than everything else either way.

## Caveats

- **Only six months of data.** Reason 1 may be partly seasonal; a year of history would separate the two.
- **History starts in April.** The "April cohort" includes everyone who was already a customer before April, so it's really "established customers," not "customers acquired in April."
- **Guest checkouts are excluded.** Rows without a CustomerID were dropped in cleaning (253 rows), so these figures are customer-attributed revenue only.
- **Small numbers.** Germany has 34–36 repeat customers; a handful of large buyers changing behaviour could drive its result. Looking at German customers individually is the natural next step.

---

## The SQL

Run the blocks in order against `data/retail.db` (e.g. `sqlite3 data/retail.db`, paste `setup`, then any query). `tests/test_report_sql.py` runs every block below against a fresh database and checks the headline numbers, so this SQL and the figures above can't silently drift apart.

```sql
-- name: setup
-- Definitions shared by every query below. TEMP views exist only for this
-- connection, so running this never changes the database file.
DROP VIEW IF EXISTS quarter_lines;
DROP VIEW IF EXISTS customer_orders;
DROP VIEW IF EXISTS repeat_lines;
DROP VIEW IF EXISTS repeat_customers;

-- Every line in Q2 or Q3 2026, tagged with its quarter.
CREATE TEMP VIEW quarter_lines AS
SELECT t.*,
       CASE WHEN invoice_date < '2026-07-01' THEN 'Q2' ELSE 'Q3' END AS qtr
FROM transactions t
WHERE invoice_date >= '2026-04-01' AND invoice_date < '2026-10-01';

-- Order counts per customer: within each quarter, and lifetime to each quarter end.
CREATE TEMP VIEW customer_orders AS
SELECT customer_id,
       MIN(country)                                                             AS country,
       substr(MIN(invoice_date), 1, 7)                                          AS cohort,  -- first-purchase month
       COUNT(DISTINCT CASE WHEN invoice_date <  '2026-07-01' THEN invoice_no END) AS orders_by_q2_end,
       COUNT(DISTINCT CASE WHEN invoice_date <  '2026-10-01' THEN invoice_no END) AS orders_by_q3_end,
       COUNT(DISTINCT CASE WHEN invoice_date >= '2026-04-01' AND invoice_date < '2026-07-01' THEN invoice_no END) AS orders_q2,
       COUNT(DISTINCT CASE WHEN invoice_date >= '2026-07-01' AND invoice_date < '2026-10-01' THEN invoice_no END) AS orders_q3
FROM transactions
GROUP BY customer_id;

-- Lines bought by a *repeat customer* in that quarter: same rule as the API,
-- i.e. 2+ orders in total by the end of the quarter.
CREATE TEMP VIEW repeat_lines AS
SELECT l.*
FROM quarter_lines l
JOIN customer_orders c USING (customer_id)
WHERE (l.qtr = 'Q2' AND c.orders_by_q2_end >= 2)
   OR (l.qtr = 'Q3' AND c.orders_by_q3_end >= 2);

-- One row per customer: repeat revenue in each quarter and how they moved.
CREATE TEMP VIEW repeat_customers AS
SELECT c.customer_id, c.country, c.cohort,
       COALESCE(SUM(CASE WHEN r.qtr = 'Q2' THEN r.revenue END), 0) AS rev_q2,
       COALESCE(SUM(CASE WHEN r.qtr = 'Q3' THEN r.revenue END), 0) AS rev_q3,
       CASE
         WHEN c.orders_by_q2_end >= 2 AND c.orders_q3 > 0 THEN 'retained'    -- repeat in both
         WHEN c.orders_by_q2_end >= 2                     THEN 'lapsed'      -- repeat in Q2, gone in Q3
         WHEN c.orders_q3 > 0 AND c.orders_by_q3_end >= 2 THEN 'new repeat'  -- became repeat in Q3
         ELSE 'never repeat'
       END AS status
FROM customer_orders c
LEFT JOIN repeat_lines r USING (customer_id)
GROUP BY c.customer_id;
```

```sql
-- name: headline
SELECT ROUND(SUM(CASE WHEN qtr = 'Q2' THEN revenue END), 2)                 AS q2_revenue,
       ROUND(SUM(CASE WHEN qtr = 'Q3' THEN revenue END), 2)                 AS q3_revenue,
       ROUND(SUM(CASE WHEN qtr = 'Q3' THEN revenue ELSE -revenue END), 2)   AS change,
       ROUND(100.0 * SUM(CASE WHEN qtr = 'Q3' THEN revenue ELSE -revenue END)
                   / SUM(CASE WHEN qtr = 'Q2' THEN revenue END), 1)         AS change_pct,
       COUNT(DISTINCT CASE WHEN qtr = 'Q2' THEN customer_id END)            AS q2_customers,
       COUNT(DISTINCT CASE WHEN qtr = 'Q3' THEN customer_id END)            AS q3_customers
FROM repeat_lines;
```

```sql
-- name: bridge
SELECT status,
       COUNT(*)                          AS customers,
       ROUND(SUM(rev_q2), 0)             AS q2_revenue,
       ROUND(SUM(rev_q3), 0)             AS q3_revenue,
       ROUND(SUM(rev_q3 - rev_q2), 0)    AS change
FROM repeat_customers
WHERE status <> 'never repeat'
GROUP BY status
ORDER BY change;
```

```sql
-- name: by_country
WITH c AS (
  SELECT country,
         SUM(CASE WHEN qtr = 'Q2' THEN revenue END)                      AS q2,
         SUM(CASE WHEN qtr = 'Q3' THEN revenue END)                      AS q3,
         COUNT(DISTINCT CASE WHEN qtr = 'Q2' THEN customer_id END)        AS cust_q2,
         COUNT(DISTINCT CASE WHEN qtr = 'Q3' THEN customer_id END)        AS cust_q3,
         1.0 * COUNT(DISTINCT CASE WHEN qtr = 'Q2' THEN invoice_no END)
             / COUNT(DISTINCT CASE WHEN qtr = 'Q2' THEN customer_id END)  AS orders_per_cust_q2,
         1.0 * COUNT(DISTINCT CASE WHEN qtr = 'Q3' THEN invoice_no END)
             / COUNT(DISTINCT CASE WHEN qtr = 'Q3' THEN customer_id END)  AS orders_per_cust_q3,
         1.0 * SUM(CASE WHEN qtr = 'Q2' THEN quantity END)
             / SUM(CASE WHEN qtr = 'Q2' THEN 1 END)                      AS units_per_line_q2,
         1.0 * SUM(CASE WHEN qtr = 'Q3' THEN quantity END)
             / SUM(CASE WHEN qtr = 'Q3' THEN 1 END)                      AS units_per_line_q3
  FROM repeat_lines
  GROUP BY country
)
SELECT country,
       ROUND(q2, 0) AS q2, ROUND(q3, 0) AS q3, ROUND(q3 - q2, 0) AS change,
       ROUND(100.0 * (q3 - q2) / q2, 1)                        AS change_pct,
       ROUND(100.0 * q2 / SUM(q2) OVER (), 1)                  AS pct_of_q2_base,
       ROUND(100.0 * (q3 - q2) / SUM(q3 - q2) OVER (), 1)      AS pct_of_total_change,
       cust_q2, cust_q3,
       ROUND(orders_per_cust_q2, 2) AS orders_per_cust_q2, ROUND(orders_per_cust_q3, 2) AS orders_per_cust_q3,
       ROUND(units_per_line_q2, 2)  AS units_per_line_q2,  ROUND(units_per_line_q3, 2)  AS units_per_line_q3
FROM c
ORDER BY change;
```

```sql
-- name: by_product
WITH p AS (
  SELECT stock_code, description,
         SUM(CASE WHEN qtr = 'Q2' THEN revenue END)   AS q2,
         SUM(CASE WHEN qtr = 'Q3' THEN revenue END)   AS q3,
         SUM(CASE WHEN qtr = 'Q2' THEN quantity END)  AS units_q2,
         SUM(CASE WHEN qtr = 'Q3' THEN quantity END)  AS units_q3
  FROM repeat_lines
  GROUP BY stock_code, description
)
SELECT stock_code, description,
       ROUND(q2, 0) AS q2, ROUND(q3, 0) AS q3, ROUND(q3 - q2, 0) AS change,
       ROUND(100.0 * (q3 - q2) / SUM(q3 - q2) OVER (), 1)   AS pct_of_total_change,
       units_q2, units_q3,
       ROUND(100.0 * (units_q3 - units_q2) / units_q2, 1)   AS units_change_pct,
       ROUND(q2 / units_q2, 2) AS price_q2, ROUND(q3 / units_q3, 2) AS price_q3
FROM p
ORDER BY change;
```

```sql
-- name: by_cohort
SELECT cohort,
       SUM(rev_q2 > 0)                                                  AS repeat_cust_q2,
       SUM(rev_q3 > 0)                                                  AS repeat_cust_q3,
       ROUND(SUM(rev_q2), 0)                                            AS q2,
       ROUND(SUM(rev_q3), 0)                                            AS q3,
       ROUND(SUM(rev_q3 - rev_q2), 0)                                   AS change,
       ROUND(100.0 * SUM(rev_q3 - rev_q2) / SUM(rev_q2), 1)             AS change_pct,
       ROUND(100.0 * SUM(rev_q2) / SUM(SUM(rev_q2)) OVER (), 1)          AS pct_of_q2_base,
       ROUND(100.0 * SUM(rev_q3 - rev_q2) / SUM(SUM(rev_q3 - rev_q2)) OVER (), 1) AS pct_of_total_change
FROM repeat_customers
GROUP BY cohort
ORDER BY cohort;
```

```sql
-- name: cohort_frequency
-- Orders per *retained* repeat customer: did the same people buy less often?
SELECT c.cohort,
       ROUND(1.0 * SUM(c.orders_q2) / COUNT(*), 2) AS orders_per_cust_q2,
       ROUND(1.0 * SUM(c.orders_q3) / COUNT(*), 2) AS orders_per_cust_q3,
       ROUND(SUM(r.rev_q2) / SUM(c.orders_q2), 2)  AS avg_order_q2,
       ROUND(SUM(r.rev_q3) / SUM(c.orders_q3), 2)  AS avg_order_q3,
       COUNT(*)                                    AS retained_customers
FROM repeat_customers r
JOIN customer_orders c USING (customer_id)
WHERE r.status = 'retained'
GROUP BY c.cohort
UNION ALL
SELECT 'all',
       ROUND(1.0 * SUM(c.orders_q2) / COUNT(*), 2), ROUND(1.0 * SUM(c.orders_q3) / COUNT(*), 2),
       ROUND(SUM(r.rev_q2) / SUM(c.orders_q2), 2),  ROUND(SUM(r.rev_q3) / SUM(c.orders_q3), 2),
       COUNT(*)
FROM repeat_customers r
JOIN customer_orders c USING (customer_id)
WHERE r.status = 'retained';
```

```sql
-- name: monthly_step_change
-- Are the Germany and product drops gradual or a cliff?
SELECT substr(invoice_date, 1, 7) AS month,
       SUM(CASE WHEN stock_code IN ('71053', '22457', '84406B') THEN quantity END)     AS big3_units,
       SUM(CASE WHEN stock_code NOT IN ('71053', '22457', '84406B') THEN quantity END) AS other_units,
       ROUND(1.0 * SUM(CASE WHEN country = 'Germany' THEN quantity END)
                 / SUM(CASE WHEN country = 'Germany' THEN 1 END), 2)                  AS germany_units_per_line,
       ROUND(1.0 * SUM(CASE WHEN country <> 'Germany' THEN quantity END)
                 / SUM(CASE WHEN country <> 'Germany' THEN 1 END), 2)                 AS others_units_per_line
FROM repeat_lines
GROUP BY month
ORDER BY month;
```

```sql
-- name: sensitivity
-- Re-run the headline numbers with a stricter rule: 2+ orders *within* the quarter.
-- If the story only held under one definition, it wouldn't be a real finding.
WITH strict_lines AS (
  SELECT l.*
  FROM quarter_lines l
  JOIN customer_orders c USING (customer_id)
  WHERE (l.qtr = 'Q2' AND c.orders_q2 >= 2) OR (l.qtr = 'Q3' AND c.orders_q3 >= 2)
)
SELECT 'Germany revenue change %' AS check_name,
       ROUND(100.0 * SUM(CASE WHEN qtr = 'Q3' THEN revenue ELSE -revenue END)
                   / SUM(CASE WHEN qtr = 'Q2' THEN revenue END), 1) AS value
FROM strict_lines WHERE country = 'Germany'
UNION ALL
SELECT 'Other countries revenue change %',
       ROUND(100.0 * SUM(CASE WHEN qtr = 'Q3' THEN revenue ELSE -revenue END)
                   / SUM(CASE WHEN qtr = 'Q2' THEN revenue END), 1)
FROM strict_lines WHERE country <> 'Germany'
UNION ALL
SELECT 'Big-3 products units change % (ex-Germany)',
       ROUND(100.0 * SUM(CASE WHEN qtr = 'Q3' THEN quantity ELSE -quantity END)
                   / SUM(CASE WHEN qtr = 'Q2' THEN quantity END), 1)
FROM strict_lines WHERE stock_code IN ('71053', '22457', '84406B') AND country <> 'Germany'
UNION ALL
SELECT 'Other products units change % (ex-Germany)',
       ROUND(100.0 * SUM(CASE WHEN qtr = 'Q3' THEN quantity ELSE -quantity END)
                   / SUM(CASE WHEN qtr = 'Q2' THEN quantity END), 1)
FROM strict_lines WHERE stock_code NOT IN ('71053', '22457', '84406B') AND country <> 'Germany'
UNION ALL
SELECT 'Total repeat revenue change %',
       ROUND(100.0 * SUM(CASE WHEN qtr = 'Q3' THEN revenue ELSE -revenue END)
                   / SUM(CASE WHEN qtr = 'Q2' THEN revenue END), 1)
FROM strict_lines;
```
