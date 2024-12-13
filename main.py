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
df = pd.read_excel('interactions.xlsx') #

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

df2 = pd.read_csv('db_drug_interactions.csv')

print(df2.head())

print(df2.shape)
print(df2.columns)
print(df2.dtypes)

print(df2['Drug 1'].unique())

# how many unique values are in the 'Drug 1' column?
print(len(df2['Drug 1'].unique()))
print(len(df2['Drug 2'].unique()))
print(len(df2['Interaction Description'].unique()))


df3 = 










# we need to perform text analysis on the 'Interaction Description' column
# to extract the drug interactions

# we will use the nltk library for text analysis
# nltk: to perform text analysis

import nltk
from nltk.corpus import stopwords

# stopwords: a list of common words that are not useful for text analysis

nltk.download('stopwords')

# Inside Interactions Description column, we have a lot of text data

# a sample entry for interaction description is:
print(df2['Interaction Description'][0])
# this is "Trioxsalen may increase the photosensitizing activities of Verteporfin."

# this means that we need to check that the first drug that is mentioned
# corresponds to the 'Drug 1' column and the second drug corresponds to the 'Drug 2' column

# we need to extract the drug names from the 'Interaction Description' column
# and check if they are present in the 'Drug 1' and 'Drug 2' columns