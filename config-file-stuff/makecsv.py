import pandas as pd
import sqlite3


df = pd.read_csv('PZSR_SUBJECT_CLASS_ROSTER.csv', dtype={'Student ID': 'object'})

new_df = pd.DataFrame()
new_df['student_id'] = df['Student ID']
new_df['username'] = df['Student Email'].str.split('@').str.get(0)
new_df['first_name'] = df['First Name']
new_df['last_name'] = df['Last Name']
new_df['course'] =  df['Class'].str.split('-').str.get(0).str.strip()
new_df['section'] =  df['Class'].str.split('-').str.get(1).str.strip()

mycourses = [
        ('CSC 135', '060'),
        ('CSC 235', '010'),
        ('CSC 447', '010'),
        ('CSC 447', '020'),
        ('CSC 447', '101'),
        ('CSC 447', '102'),
        ('CSC 242', '990')
        ]

query_strings = ["(course == '{}' and section == '{}')".format(c,s) for c,s in mycourses]
query_string = ' or '.join(query_strings)

new_df = new_df.query(query_string)

new_df.to_csv('roster.csv', index=False)

