import pandas as pd
from time import sleep
import requests
from requests.exceptions import Timeout
from os.path import exists
import json

# Read in csv (downloaded from Cambridge's Open Data Portal)
df = pd.read_csv('seeclickfix.csv')

# Get a list of all icy or unshoveled sidewalks created since 12/01/19
df.head()
snowy = df[df['issue_type'] == 'Icy or Unshoveled Sidewalk']
print(snowy.shape)

# Iterate through each case
comments = {}
if exists('see_click_fix_comments.json'):

    print("loading cached comments")
    with open('see_click_fix_comments.json') as json_file:
        comments = json.load(json_file)

count = 0
cutoff = 200

successfully_queried = 0
timed_out = 0
for index, row in snowy.iterrows():
    if str(row['ticket_id']) in comments.keys():
        continue

    if count >= cutoff or timed_out > 10:
        break
    print(row['ticket_id'])
    count += 1
    prefix = 'https://seeclickfix.com/api/v2/issues/'

    response = requests.get(prefix + str(row['ticket_id']) + '/comments')
    if response.status_code == 200:
        comments[row['ticket_id']] = [{
            'comment': x['comment'],
            'created_at': x['created_at']
        } for x in response.json()['comments']]

        successfully_queried += 1
#        if count % 20 == 0:
#            sleep(20)
    else:
        print(response)
        timed_out += 1
#        break
        sleep(30)

with open('see_click_fix_comments.json', 'w') as outfile:
    json.dump(comments, outfile)

print("Successfully queried:" + str(successfully_queried))
print("Total cached:" + str(len(comments.keys())))
print("Total remaining:" + str(snowy.shape[0] - len(comments.keys())))


