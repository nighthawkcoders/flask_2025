from flask_restful import Resource
from datetime import datetime
import requests
from __init__ import app

class GitHubUser(Resource):
    def get(self, uid):
        url = app.config['GITHUB_API_URL'] + f'/users/{uid}'
        token = app.config['GITHUB_TOKEN']
        if not token:
            # assume Test Server and not using GitHub API  
            return {'message': 'GITHUB_TOKEN not set'}, 200

        try:
            headers = {'Authorization': f'token {token}'}
            response = requests.get(url, headers=headers)

            if response.status_code == 404:
                return {'message': f'Invalid UID {uid}'}, 404
            elif response.status_code != 200:
                return {'message': 'GitHub API failed to fetch user data'}, response.status_code

            return response.json(), 200

        except Exception as e:
            return {'message': str(e)}, 500
    
    def get_profile_links(self, uid):
        user_data, status_code = self.get(uid)
        if status_code != 200:
            return user_data, status_code
        
        profile_links = {
            'profile_url': user_data.get('html_url'),
            'repos_url': user_data.get('repos_url')
        }
        return profile_links, 200

    def make_github_graphql_request(self, query, variables):
        url = "https://api.github.com/graphql"
        token = app.config['GITHUB_TOKEN']
        
        if not token:
            return {'message': 'GITHUB_TOKEN not set'}, 400

        headers = {'Authorization': f'bearer {token}'}
        try:
            response = requests.post(url, json={'query': query, 'variables': variables}, headers=headers)
            
            if response.status_code != 200:
                return {'message': 'GitHub API failed to fetch data'}, response.status_code

            return response.json(), 200
        except Exception as e:
            return {'message': str(e)}, 500

    def get_commit_stats(self, uid, start_date_str, end_date_str):
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        start_date_iso = start_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        end_date_iso = end_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        
        total_commit_query = """
        query($login: String!, $from: DateTime!, $to: DateTime!) {
            user(login: $login) {
                contributionsCollection(from: $from, to: $to) {
                    totalCommitContributions
                }
            }
        }
        """
        total_commit_variables = {
            "login": uid,
            "from": start_date_iso,
            "to": end_date_iso
        }
        
        total_commit_data, total_commit_status_code = self.make_github_graphql_request(total_commit_query, total_commit_variables)
        total_commits = 0
        if total_commit_status_code == 200:
            total_commits = total_commit_data['data']['user']['contributionsCollection']['totalCommitContributions']

        detailed_commit_query = """
        query($login: String!, $from: DateTime!, $to: DateTime!) {
            user(login: $login) {
                contributionsCollection(from: $from, to: $to) {
                    commitContributionsByRepository {
                        repository {
                            nameWithOwner
                        }
                        contributions(first: 100) {
                            nodes {
                                commitCount
                                occurredAt
                            }
                        }
                    }
                }
            }
        }
        """
        detailed_commit_variables = {
            "login": uid,
            "from": start_date_iso,
            "to": end_date_iso
        }
        
        detailed_commit_data, detailed_commit_status_code = self.make_github_graphql_request(detailed_commit_query, detailed_commit_variables)
        details_of_commits = []
        if detailed_commit_status_code == 200:
            details_of_commits = detailed_commit_data['data']['user']['contributionsCollection']['commitContributionsByRepository']
        
        return {
            'total_commit_contributions': total_commits,
            'details_of_commits': details_of_commits
        }, 200

    def get_pr_stats(self, uid, start_date_str, end_date_str):
        query = """
        query($query: String!) {
            search(query: $query, type: ISSUE, first: 100) {
                edges {
                    node {
                        ... on PullRequest {
                            title
                            url
                            createdAt
                            repository {
                                nameWithOwner
                            }
                            author {
                                login
                            }
                            comments(first: 10) {
                                nodes {
                                    body
                                    author {
                                        login
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        """
        search_query = f"type:pr author:{uid} created:{start_date_str}..{end_date_str}"
        variables = {
            "query": search_query
        }
        data, status_code = self.make_github_graphql_request(query, variables)
        if status_code != 200:
            return data, status_code

        pr_stats = data['data']['search']['edges']

        return {'pull_requests': pr_stats}, 200

    def get_issue_stats(self, uid, start_date_str, end_date_str):
        query = """
        query($query: String!) {
            search(query: $query, type: ISSUE, first: 100) {
                edges {
                    node {
                        ... on Issue {
                            title
                            url
                            createdAt
                            repository {
                                nameWithOwner
                            }
                            author {
                                login
                            }
                            comments(first: 10) {
                                nodes {
                                    body
                                    author {
                                        login
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        """
        search_query = f"type:issue author:{uid} created:{start_date_str}..{end_date_str}"
        variables = {
            "query": search_query
        }
        data, status_code = self.make_github_graphql_request(query, variables)
        if status_code != 200:
            return data, status_code

        issue_stats = data['data']['search']['edges']
        return {'issues': issue_stats}, 200


class GitHubOrg(Resource):
    def get_users(self, org_name):
        url = app.config['GITHUB_API_URL'] + f'/orgs/{org_name}/members'
        token = app.config['GITHUB_TOKEN']
        if not token:
            return {'message': 'GITHUB_TOKEN not set'}, 400

        try:
            headers = {'Authorization': f'token {token}'}
            response = requests.get(url, headers=headers)

            if response.status_code != 200:
                return {'message': 'GitHub API failed to fetch organization members'}, response.status_code

            return response.json(), 200

        except Exception as e:
            return {'message': str(e)}, 500

    def get_repos(self, org_name):
        url = app.config['GITHUB_API_URL'] + f'/orgs/{org_name}/repos'
        token = app.config['GITHUB_TOKEN']
        if not token:
            return {'message': 'GITHUB_TOKEN not set'}, 400

        try:
            headers = {'Authorization': f'token {token}'}
            response = requests.get(url, headers=headers)

            if response.status_code != 200:
                return {'message': 'GitHub API failed to fetch organization repositories'}, response.status_code

            return response.json(), 200

        except Exception as e:
            return {'message': str(e)}, 500
