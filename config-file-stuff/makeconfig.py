from pprint import pprint
import pandas as pd
import json

CONFIG = {
    "submission_basedir": "/home/kutztown.edu/schwesin/private/submissions/2218",
    "assignments": {},
    "roster": {},
    "email": "schwesin@kutztown.edu"
    }

df = pd.read_csv('roster.csv')

coursenames = df['course'].unique()

for course in coursenames:
    name = ''.join(course.split()).lower()
    CONFIG["assignments"][name] = []
    CONFIG["roster"][name] = []

    cdf = df.query("course == '{}'".format(course))
    usernames = list(cdf["username"])
    for user in usernames:
        CONFIG["roster"][name].append(user)

json_string = json.dumps(CONFIG, indent=4)
print(json_string)

