import requests
import json

"""
Script gets all closed pull requests (PR) and writes them to a JSON file.
"""

# Specify the repository owner, repository name, and GitHub access token
owner = 'monkeytypegame'
repo = 'monkeytype'
access_token = 'SECRET'

# Specify the API endpoint for retrieving PRs
api_url = f'https://api.github.com/repos/{owner}/{repo}/pulls'

# Set headers for API request
headers = {
    'Accept': 'application/vnd.github+json',
    'Authorization': 'Bearer ' + access_token,
    'X-GitHub-Api-Version': '2022-11-28'
}

# Initialize empty lists
all_PR_numbers = []
all_pull_requests = []

# Loop to retrieve all the pages of PRs
page = 1
while True:
    # Make a request to the GitHub API to retrieve the closed PRs for the current page (max per_page is 100)
    response = requests.get(api_url, headers=headers, params={'state': 'closed', 'page': page, 'per_page': 100})

    # Check the response status code
    if response.status_code == 200:
        # Parse the JSON response
        pull_requests = json.loads(response.text)

        # Append each PR number
        for pr in pull_requests:
            all_PR_numbers.append(pr["number"])

        # Check if there are more pages of PRs
        if 'Link' in response.headers and 'rel="next"' in response.headers['Link']:
            # Extract the URL for the next page of results from the Link header
            next_page_url = response.headers['Link'].split(';')[0].strip('<>')
            api_url = next_page_url
            page += 1
        else:
            # Break the loop if there are no more pages of results
            break
    else:
        # Print an error message if the request fails
        print(f'Failed to retrieve pull requests: Status code: {response.status_code}')
        break


# Loop through each PR number and make an API request
for pr_number in all_PR_numbers:
    # Format the API URL with the PR number
    pr_url = f'https://api.github.com/repos/{owner}/{repo}/pulls/' + str(pr_number)
    
    # Make a request to the GitHub API to retrieve the PR information
    response = requests.get(pr_url, headers=headers)
    
    # Check if the API request was successful
    if response.status_code == 200:
        # Retrieve the PR information from the API response
        PR = response.json()

        # Extract only the desired fields from the PR information
        selected_PR = {
            'title': PR['title'],
            'body': PR['body'],
            'created_at': PR['created_at'],
            'closed_at': PR['closed_at'],
            'merged_at': PR['closed_at'],
            'author_association': PR['author_association'],
            'merged': PR['merged'],
            'num_comments': PR['comments'],
            'num_review_comments': PR['review_comments'],
            'num_commits': PR['commits'],
            'num_additions': PR['additions'],
            'num_deletions': PR['deletions'],
            'num_changed_files': PR['changed_files'],
            'first_response_at': ''
        }

        # Get comments for the pull request
        comments_response = requests.get(PR['comments_url'], headers=headers, params={'sort': 'created', 'direction': 'asc'})
        if comments_response.status_code == 200:
            comments = comments_response.json()

             # Iterate through the comments to find the first one that is not made by the contributor
            for comment in comments:
                # Check if the comment is not made by the contributor
                if comment['user']['login'] != PR['user']['login']:
                    # Extract the desired fields from the comment
                    selected_PR['first_response_at'] = comment['created_at']
                    break  # Break out of the loop after finding the first comment not made by the contributor
        
        all_pull_requests.append(selected_PR)
    else:
        print(f"Failed to retrieve pull request {pr_number}. Status code: {response.status_code}")


# Save the retrieved PRs to a JSON file
with open('data/pull_requests.json', 'w') as f:
    json.dump(all_pull_requests, f)

# Print the total number of PRs retrieved
print(f'Total number of pull requests: {len(all_pull_requests)}')
print(f'Pull requests saved to pull_requests.json')
