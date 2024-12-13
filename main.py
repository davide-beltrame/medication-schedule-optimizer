# SOFTWARE ENGINEERING PROJECT
# A python tool that optimizes medication schedules 
# by analyzing drug prescriptions highlighting interactions and compatibility.
#  Input (drug names, frequency, and optional patient parameters) is standardized 
# via a parser and computed through an optimizer 
# based on a drug interactions dataset 
# to output a user-friendly schedule.

# our dataset is in .xlsx format
# we will use pandas to read the dataset


# required libraries
# pandas: to read the dataset
# openpyxl: to read .xlsx files


import pandas as pd

# read the dataset
df = pd.read_excel('interactions.xlsx')

# print the first 5 rows of the dataset
print(df.head())

# print the shape of the dataset
print(df.shape)

# print the columns of the dataset
print(df.columns)

# print the data types of the columns
print(df.dtypes)

# print all unique values in the 'Drug_A' and 'Drug_B' columns
print(df['Drug_A'].unique())
