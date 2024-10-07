# Fetch Rewards Online Assessment
# Step 1 - Building the Relational Data Model
Refer to the file: Database ERD.pdf

For this step, I investigated the Receipts, Users, and Brand data provided. For this, I used a simple data reader function in Python to read from the gzip file and parse out the json objects to be reviewed. I made some assumptions during the ERD development and made note of those in the given sticky notes included in the PDF image. Along with that, I made the decision to change the _id field to a more readable field name. Those were: usersKey, brandsKey, and receiptsKey. This was also to avoid confusion with FK joins, such as Receipts.userId and Users.usersKey. Additionally, I added a Transactions table as a form of a junction table to make simpler, more efficient joins between unlinked tables.

# Step 2 - Answering Stakeholder Questions With SQL
Refer to the file: query_questions.sql

All questions are answered in order in this file using MySQL dialect. Comments are included at the start of each to outline the solutioning and idea behind the steps of each query.

# Step 3 - Data Quality Analysis
Refer to the file: data_quality_check.py

This file exemplifies some standard data quality issues I would check in an initial ingest, profiling, validation stage in a data platfrom. This included:
  1) Initial data exploration
  2) NULL Checks
  3) Duplicate key checks
  4) Data Consistency - ensuring data received matched parameters outlined in the problem statement for given fields, data type checks, current date checks, etc.
  5) Outlier Checks (with plots)
  6) Orphaned Records analysis

Each of these was explored and given some comments for rationale behind the check needed as well as ideas for follow up investigation/solutioning. This did not include fixes or comprehensive analysis of the problem in each case, but was used to highlight areas of concern.

# Step 4 - Email to Stakeholder
Refer to the file: Stakeholders Email.txt
