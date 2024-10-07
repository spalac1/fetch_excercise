import pandas as pd
import numpy as np
import shutil
import gzip
import matplotlib.pyplot as plt
from datetime import datetime


# General rules to check for
# check for NULLs
# check data types match for columns
# check for duplicates
# check for outliers (numeric fields)
# check that values map correctly (i.e. correct value with correct column (presumably))

def read_corrupted_json(file, skiprows=None):
    with open(file) as f:
        if skiprows:
            f.readlines(skiprows)
        df = pd.read_json(f, lines=True)
    return df

def check_percentage_null(df, threshold=0):
    for col, percent_null in df.isnull().mean().items():
        if percent_null > threshold:
            print(f'{col}: {round(percent_null*100,2)}% of this column is NULL')

def convert_date(x):
    try:
        return(datetime.utcfromtimestamp(int(x['$date'])/1000).strftime('%Y-%m-%d %H:%M:%S'))
    except TypeError as e:
        print(f'Error while converting datetime: {e}')


all_files = ['brands.json.gz','receipts.json.gz','users.json.gz']

# Commenting out for now as it is causing the error when reading json. Manually manipulating file to remove issue
# for i in all_files:
#   if 'json' in i:
#     with gzip.open(f'data/{i}', 'rb') as f_in:
#           with open(i.replace('.gz',''), 'wb') as f_out:
#             shutil.copyfileobj(f_in, f_out)
     

receipts_df = read_corrupted_json('receipts.json')
brands_df = read_corrupted_json('brands.json')

# Got a strange string that caused malformed json data after above file open/read/write function. Deleted line for the time being to be able to read in correct data
users_df = read_corrupted_json('users.json',skiprows=1)

all_df_names = ['receipts_df', 'brands_df', 'users_df']

# Step 0: basic table structure, make sure we can read from dataframes, and clean up some records that were read in by pd.read_json() for better analysis in the future
print('\n')
print(receipts_df.head())
print('\n')
print(brands_df.head())
print('\n')
print(users_df.head())

# Can be used to see data types if needed
# print(receipts_df.info())
# print(brands_df.info())
# print(users_df.info())

print(f'\nreceipts_df has {receipts_df.shape[0]} rows and {receipts_df.shape[1]} columns')
print(f'brands_df has {brands_df.shape[0]} rows and {brands_df.shape[1]} columns')
print(f'users_df has {users_df.shape[0]} rows and {users_df.shape[1]} columns')

# remove dictionary values from columns
receipts_df['_id'] = receipts_df['_id'].apply(lambda x: x['$oid'])
brands_df['_id'] = brands_df['_id'].apply(lambda x: x['$oid'])
users_df['_id'] = users_df['_id'].apply(lambda x: x['$oid'])

# apply datetime fromatting
receipts_df['createDate'] = receipts_df['createDate'].apply(lambda x: convert_date(x) if pd.notna(x) else x)
receipts_df['dateScanned'] = receipts_df['dateScanned'].apply(lambda x: convert_date(x) if pd.notna(x) else x)
receipts_df['finishedDate'] = receipts_df['finishedDate'].apply(lambda x: convert_date(x) if pd.notna(x) else x)
receipts_df['modifyDate'] = receipts_df['modifyDate'].apply(lambda x: convert_date(x) if pd.notna(x) else x)
receipts_df['pointsAwardedDate'] = receipts_df['pointsAwardedDate'].apply(lambda x: convert_date(x) if pd.notna(x) else x)
receipts_df['purchaseDate'] = receipts_df['purchaseDate'].apply(lambda x: convert_date(x) if pd.notna(x) else x)
users_df['createdDate'] = users_df['createdDate'].apply(lambda x: convert_date(x) if pd.notna(x) else x)
users_df['lastLogin'] = users_df['lastLogin'].apply(lambda x: convert_date(x) if pd.notna(x) else x)

# Step 1: Check for NULL data
# Use above shape values for relative comparison
print(receipts_df.isnull().sum())
print(brands_df.isnull().sum())
print(users_df.isnull().sum())

# Seems like a lot of NULLs. Let's check percentage NULL values for columns with > 1% NULL
print('\nreceipts_df')
check_percentage_null(receipts_df, threshold=0)
print('\nbrands_df')
check_percentage_null(brands_df, threshold=0)
print('\nusers_df')
check_percentage_null(users_df, threshold=0)

# So we are seeing a lot of NULL values for quite a few fields. Next would be asking ourselves (and whoever provided us this data): is it logical for these values to be NULL.
# For the following fields, I would say we could reasonably expect NULL values
# receipts
# -- bonusPointsEarned
# -- bonusPointsEarnedReason
# -- finishedDate
# -- pointsAwardedDate
# -- pointsEarned
# -- rewardsReceiptItemList

# Fields we would expect to always see values and would need to follow up on
# -- purchaseDate
# -- purchasedItemCount
# -- totalSpent


# brands
# -- category
# -- categoryCode
# -- topBrand
# -- brandCode


# users
# -- signUpSource
# -- State

# Fields we should follow up on
# -- lastLogin 



# Step 2: Check for duplicates
# This could require updates, but at least for now, we check just on the subset of ID
duplicate_receipts = receipts_df[receipts_df.duplicated(subset=['_id'])]
print('\n')
print(duplicate_receipts)
# returned nothing, so no follow up

duplicate_brands = brands_df[brands_df.duplicated(subset=['_id'])]
print(duplicate_brands)
# returned nothing, so no follow up

duplicate_users = users_df[users_df.duplicated(subset=['_id'])]
print(duplicate_users.shape)
# returned 282 rows, so there are duplicate records, will need follow up but can clean by dropping duplicates for now
users_df.drop_duplicates(inplace=True)
duplicate_users = users_df[users_df.duplicated(subset=['_id'])]
print(duplicate_users.shape)




# Step 3: Data Consistency
# check states are all 2 letter codes and strings
# check all users.role == consumer; based on requirements, all should be, but we have other values, so needs cleaning
# check distinct values of all other columns to make sure there is consistency (should be able to loop quickly)

print('\n')
# Identify outliers in totalSpent
print(receipts_df['totalSpent'].describe())
print(f"Max total spent value is: {max(receipts_df['totalSpent'])}")
# Notice that the max value is far larger than others, causing huge standard deviation
# could be an invalid value and needs to be reviewed
print('\n')

# Check for receipts with totalSpent < 0 for invalid negative values
print('Check valid total Spent amounts')
print(receipts_df[receipts_df['totalSpent'] < 0])
print('\n')

# Check for future purchase dates can be used for other dates as well
# The following comparison can also be used to check other dates
print("Check that dates can't be in the future")
print(receipts_df[receipts_df['purchaseDate'] > datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
print('\n')

# Check the data types of columns
# Could then use this for further analysis of whether or not row values match the data type specified by the column
print(receipts_df.dtypes)

# Check if rewardsReceiptStatus contains only expected values
# Based on the provided criteria, these all look ok
print(receipts_df['rewardsReceiptStatus'].unique())
print('\n')

# Check that all state values are strings and 2 character codes and that codes are valid
print(users_df['state'].unique())
# All present codes are valid, but we do have some NAs. If this is an optional field for a user to enter, this is ok. If not, we would need to follow up with the client as needed
print('\n')

# As noted in our prompt, role should have hard coded value of CONSUMER. If not, we should identify what values we are receiving and determine if there is a fix needed
print('Check valid values for user.role')
print(users_df[users_df['role'].apply(lambda x: x.lower()) != 'consumer'])
# From the above, we seem to have 8 values set to fetch-staff. This could be internal testing use and ok, or could be an error. Will need to discuss and determine resolution


# Visualize distributions of totalSpent
receipts_df['totalSpent'].hist()
plt.show()
# This plot can further show how we have some outlying data that needs to be investigated

fig = plt.figure(figsize=(15,5))
plt.boxplot(receipts_df[receipts_df['purchasedItemCount'].notnull()]['purchasedItemCount'])
plt.show()

print('\n')
# Step 4: Check for orphaned records. Do we have any PK/FKs that don't match anywhere else?
# The below logic can be extrapolated and used for other PK/FK relationships
merged_df = pd.merge(receipts_df, users_df, how='left', left_on='userId', right_on='_id', indicator=True)
orphaned_receipts = merged_df[merged_df['_merge'] == 'left_only']
print(orphaned_receipts.shape)
print(orphaned_receipts[['userId','_id_y']].head())
# This shows us that we have 148 records in the receipts dataset with user Ids not found in the users dataset. This can be a large problem in future join logic as a potential issue in understanding the relationships as a whole


