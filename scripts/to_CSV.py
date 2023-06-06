import csv
import json
import math 
from datetime import datetime

"""
Script preprocesses the data to get it in form suitable for our analyses and writes it in a CSV format.
"""

# Load the JSON data from a file
with open('data/pull_requests.json', 'r') as file:
    PRs = json.load(file)

# Create a CSV writer to write data to a CSV file
f = csv.writer(open("data/dataset.csv", "w"))

# Write CSV header - time_to_first_response might need to be changed
f.writerow([ 'description_length', 'merged', 'time_to_close', 'time_to_merge', 'time_to_first_response',
             'author_association', 'num_comments', 'num_review_comments', 'num_commits', 'num_additions',
             'num_deletions', 'num_changed_lines', 'num_changed_files' ])

num_outliers = 0

# Iterate over each pull request
for PR in PRs:
    # Calculate title + body wordcount
    title = PR['title'] if PR['title'] else ''
    body = PR['body'] if PR['body'] else ''
    description = title + ' ' + body
    description_length = len(description.split())
    
    # Convert the date strings to datetime objects
    created_at = datetime.strptime(PR['created_at'], "%Y-%m-%dT%H:%M:%SZ")
    closed_at = datetime.strptime(PR['closed_at'], "%Y-%m-%dT%H:%M:%SZ")
    merged_at = datetime.strptime(PR['merged_at'], "%Y-%m-%dT%H:%M:%SZ")
    if PR['first_response_at'] != '':
        first_response_at = datetime.strptime(PR['first_response_at'], "%Y-%m-%dT%H:%M:%SZ")
    else:
        first_response_at = created_at

    # Calculate time differences
    time_to_close = closed_at - created_at
    time_to_merge = merged_at - created_at
    time_to_first_response = first_response_at - created_at

    # Extract the total hours from the time difference
    time_to_close_hours = math.floor(time_to_close.total_seconds() / 3600)
    time_to_merge_hours = math.floor(time_to_merge.total_seconds() / 3600)
    time_to_first_response_hours = math.floor(time_to_first_response.total_seconds() / 3600)
    
    # Calculate number of lines changed
    num_changed_lines = PR['num_additions'] + PR['num_deletions']

    # Remove some outliers from the dataset
    if num_changed_lines < 5000 and description_length < 4000 and time_to_merge_hours < 4000:
        # Write CSV row
        f.writerow([ description_length, PR['merged'], time_to_close_hours, time_to_merge_hours, 
                    time_to_first_response_hours, PR['author_association'], PR['num_comments'], PR['num_review_comments'],
                    PR['num_commits'], PR['num_additions'], PR['num_deletions'], num_changed_lines, PR['num_changed_files'] ])
    else:
        num_outliers += 1

print(f'Number of outliers removed: {num_outliers}')