-- What are the top 5 brands by receipts scanned for most recent month?
-- Get latest month by running max() agg function on the purchaseDate field. Use CTE to determine defined list of receipts needed for this comparison. Bonus of this is that we now no longer need to do a full table scan for final results
-- Note that this solution assumes that purchaseDate is some form of YYYY-MM-DD, so we truncate to just include month and year when getting our max to avoid maxing on the day
-- join to receipts, transactions, and brands using key values since they are indexed --> faster join and table scan
-- Note that the other option would be to join to receipt_items, but that would require a join to brands via barcode field, which is VARCHAR, and not indexed in brands, so will be slow
-- to get top 5, simply get a count of receipts by key, order in descending order, then limit to 5 records to be returned
WITH LATEST_MONTH_RECEIPT AS (
    SELECT receiptKey
    FROM Receipts
    WHERE DATE_FORMAT(purchaseDate, '%Y-%m') = (
            SELECT DATE_FORMAT(MAX(purchaseDate), '%Y-%m')
            FROM Receipts
        )
)
SELECT b.brandCode, b.name, COUNT(r.receiptKey)
FROM LATEST_MONTH_RECEIPT lmr
JOIN Receipts r
    ON lmr.receiptKey = r.receiptKey
JOIN Transactions t
    ON t.receiptKey = r.receiptKey
JOIN Brands b
    ON b.brandKey = t.brandKey
GROUP BY b.brandCode, b.name
ORDER BY COUNT(r.receiptKey) DESC
LIMIT 5
;


-- How does the ranking of the top 5 brands by receipts scanned for the recent month compare to the ranking for the previous month?
-- Either do a RANK window function or two separate queries (use the one above and then for previous month, query will have a DATEADD function on purchaseDate)
-- First, use two separate CTEs to determine the receiptKeys for the respective months needed for comparison (current month and previous month)
-- Second, using those two CTEs, determine the receipt counts from the receipts table using only keys determined from the first two CTEs
-- Third, combine the two count CTEs using a UNION ALL in order to get all data necessary for ordering and comparison
-- Fourth, Rank each brand by receipt count, grouping by month type (i.e. last month or current month). Done by simply getting row number and ordering
-- Finally, select all the above data and limit to where rank is 5 or less, essentially giving us our top 5 brands for each month
WITH LATEST_MONTH_RECEIPT AS (
    SELECT receiptKey
    FROM Receipts
    WHERE DATE_FORMAT(purchaseDate, '%Y-%m') = (
            SELECT DATE_FORMAT(MAX(purchaseDate), '%Y-%m')
            FROM Receipts
        )
), LAST_MONTH_RECEIPT AS (
    SELECT receiptKey
    FROM Receipts
    WHERE DATE_FORMAT(purchaseDate, '%Y-%m') = (
            SELECT DATE_FORMAT(DATEADD(month, -1, MAX(purchaseDate)), '%Y-%m')
            FROM Receipts
        )
), LATEST_MONTH_COUNTS AS (
    SELECT b.name AS BRAND_NAME, b.brandCode AS BRAND_CODE, COUNT(r.receiptKey) AS RECEIPT_COUNT, 'Most Recent Month' AS MONTH_TYPE
    FROM LATEST_MONTH_RECEIPT lmr
    JOIN Receipts r
        ON lmr.receiptKey = r.receiptKey
    JOIN Transactions t
        ON t.receiptKey = r.receiptKey
    JOIN Brands b
        ON b.brandKey = t.brandKey
    GROUP BY b.brandCode, b.name
), LAST_MONTH_COUNTS AS (
    SELECT b.name AS BRAND_NAME, b.brandCode AS BRAND_CODE, COUNT(r.receiptKey) AS RECEIPT_COUNT, 'Previous Month' AS MONTH_TYPE
    FROM LAST_MONTH_RECEIPT lastmr
    JOIN Receipts r
        ON lastmr.receiptKey = r.receiptKey
    JOIN Transactions t
        ON t.receiptKey = r.receiptKey
    JOIN Brands b
        ON b.brandKey = t.brandKey
    GROUP BY b.brandCode, b.name
), ALL_COUNTS AS (
    SELECT * 
    FROM LATEST_MONTH_COUNTS

    UNION ALL

    SELECT * 
    FROM LAST_MONTH_COUNTS
), FINAL AS (
    SELECT 
        BRAND_NAME, 
        BRAND_CODE, 
        RECEIPT_COUNT, 
        MONTH_TYPE,
        ROW_NUMBER() OVER (PARTITION BY MONTH_TYPE ORDER BY RECEIPT_COUNT DESC) AS RANK
    FROM ALL_COUNTS
)
SELECT RANK, BRAND_NAME, BRAND_CODE, RECEIPT_COUNT, MONTH_TYPE
FROM FINAL
WHERE RANK <= 5
ORDER BY MONTH_TYPE, RANK
;


-- When considering average spend from receipts with 'rewardsReceiptStatus’ of ‘Accepted’ or ‘Rejected’, which is greater?
-- This could either be one query with all logic or two simple queries
-- opting for one large query because most people will not want to do comparison on their own, they just want the answer
-- Below will do the average calcs for both statuses, combine them into one temp table with UNION, then we get the max of those two and return the status and average amount
WITH AVG_SPEND_PER_STATUS AS (
    SELECT rewardsReceiptStatus, AVG(totalSpent) AS AVG_SPENT
    FROM Receipts
    WHERE rewardsReceiptStatus IN ('ACCEPTED', 'REJECTED')
    GROUP BY rewardsReceiptStatus
)
SELECT *
FROM AVG_SPEND_PER_STATUS
ORDER BY AVG_SPENT DESC
LIMIT 1;



-- When considering total number of items purchased from receipts with 'rewardsReceiptStatus’ of ‘Accepted’ or ‘Rejected’, which is greater?
-- This can be a copy of the above query and logic, but substitute SUM() agg function for AVG() in CTE query
WITH TOT_PURCHASED_PER_STATUS AS (
    SELECT rewardsReceiptStatus, SUM(purchasedItemCount) AS TOT_PURCHASED
    FROM Receipts
    WHERE rewardsReceiptStatus IN ('ACCEPTED', 'REJECTED')
    GROUP BY rewardsReceiptStatus
)
SELECT *
FROM TOT_PURCHASED_PER_STATUS
ORDER BY TOT_PURCHASED DESC
LIMIT 1
;


-- Which brand has the most spend among users who were created within the past 6 months?
-- Use Transaction table as junction table to join to Receipts and Brands from Users using PK and FK fields. Much more efficient than joining Users to Receipts, then receipts to receipt_items, then receit_items to brands
-- Get SUM() of totalSpent per receipt and add WHERE clause to filter users.createdDate by the current timestamp the query was run minus 6 months
SELECT b.name, b.brandCode, SUM(r.totalSpent) TOTAL_SPENT_PER_BRAND
FROM Users u
JOIN Transactions t
    ON u.userKey = t.userKey
JOIN Brands b 
    ON b.brandKey = t.brandKey
JOIN Receipts r
    ON r.receiptKey = t.receiptKey
WHERE u.createdDate >= DATEADD(month, -6, GETDATE())
GROUP BY b.name, b.brandCode
ORDER BY TOTAL_SPENT_PER_BRAND DESC
LIMIT 1
;


-- Which brand has the most transactions among users who were created within the past 6 months?
-- The below query uses similar logic as above, but instead we simply count the number of distinct receipt IDs to get transaction count
-- necessary to include distinct ids in case a receipt shows dupes
SELECT b.name, b.brandCode, COUNT(DISTINCT t.receiptKey) TOTAL_TRANSACTIONS_PER_BRAND
FROM Users u
JOIN Transactions t
    ON u.userKey = t.userKey
JOIN Brands b 
    ON b.brandKey = t.brandKey
WHERE u.createdDate >= DATEADD(month, -6, GETDATE())
GROUP BY b.name, b.brandCode
ORDER BY TOTAL_TRANSACTIONS_PER_BRAND DESC
LIMIT 1
;