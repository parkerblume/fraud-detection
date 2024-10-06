import os
import re
from difflib import get_close_matches
import csv
import pandas as pd
from fuzzywuzzy import fuzz, process

# Initialize an empty dictionary for the name mapping
name_mapping = {}

# Read the company database CSV file
with open('data/company_database.csv', 'r', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        official_name = row['Company Name'].strip().upper()
        # Add the official name to the mapping
        name_mapping[official_name] = official_name
        # Get alternative names and split them if there are multiple
        alternative_names = row['Alternative Name(s)']
        if alternative_names:
            alternatives = [alt.strip().upper() for alt in alternative_names.split(',')]
            for alt_name in alternatives:
                name_mapping[alt_name] = official_name

# Convert the keys of the name mapping to a list for fuzzy matching
company_names = list(name_mapping.keys())

#read and combine fortune1000 and INC5000 data
df1 = pd.read_csv('data/fort1000.csv')
df2 = pd.read_csv('data/inc5000.csv')

fort1000comp = df1['Company'].tolist()


inc5000comp = df2['name'].tolist()

#combine the two lists
comps = fort1000comp + inc5000comp + company_names
comps = list(set(comps))
comps = [x.upper() for x in comps]

# fuzzy check is subway in the list
result = process.extractOne('subway', comps, scorer=fuzz.token_set_ratio, score_cutoff=20)

df = pd.read_csv('data/transactions.csv')

name_column = df['Name']

for name in name_column:
    name_upper = name.strip().upper()
    result = process.extractOne(name_upper, comps, scorer=fuzz.token_set_ratio, score_cutoff=80)
    
    if result is not None:
        match, score = result
        print(f"Original Name: {name} - Closest Match: {match} - Score: {score}")
    else:
        print(f"Original Name: {name} - No close match found - Potential Fraud!")

