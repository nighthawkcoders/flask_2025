from flask import Blueprint, request, jsonify, g
from flask_restful import Api, Resource
from flask_login import current_user, login_required
from datetime import datetime
from api.jwt_authorize import token_required
from model.github import GitHubUser, GitHubOrg
from model.user import User
import time



analytics_api = Blueprint('analytics_api', __name__, url_prefix='/api/analytics')
api = Api(analytics_api)

def get_date_range(body):
    start_date = body.get('start_date')
    end_date = body.get('end_date')
    
    if not start_date or not end_date:
        today = datetime.today()
        year = today.year

        if today >= datetime(year, 6, 15) and today <= datetime(year, 11, 14):
            start_date = datetime(year, 6, 1)
            end_date = datetime(year, 11, 14)
        elif today >= datetime(year, 11, 15) or today <= datetime(year, 3, 14):  # Fix for year transition
            if today.month < 6:  # Adjust year for early months (Jan–Mar)
                year -= 1  
            start_date = datetime(year, 9, 1)
            end_date = datetime(year + 1, 3, 14)
        elif today >= datetime(year, 4, 15) and today <= datetime(year, 6, 14):
            start_date = datetime(year, 4, 1)
            end_date = datetime(year, 6, 14)
        else:
            raise ValueError('Date is out of the defined trimesters')

        start_date = start_date.strftime('%Y-%m-%d')
        end_date = end_date.strftime('%Y-%m-%d')

    return start_date, end_date

class GitHubUserAPI(Resource):
    @token_required()
    def get(self):
        try:
            current_user = g.current_user
            github_user_resource = GitHubUser()
            response = github_user_resource.get(current_user.uid)
            
            if response[1] != 200:
                return response

            return jsonify(response[0])
        except Exception as e:
            return {'message': str(e)}, 500

class UserProfileLinks(Resource):
    @token_required()
    def get(self):
        try:
            current_user = g.current_user
            github_user_resource = GitHubUser()
            response = github_user_resource.get_profile_links(current_user.uid)
            
            if response[1] != 200:
                return response

            return jsonify(response[0])
        except Exception as e:
            return {'message': str(e)}, 500

class UserCommits(Resource):
    @token_required()
    def get(self):
        try:
            current_user = g.current_user
            try:
                body = request.get_json()
            except Exception as e:
                body = {}
            
            start_date, end_date = get_date_range(body)

            github_user_resource = GitHubUser()
            response = github_user_resource.get_commit_stats(current_user.uid, start_date, end_date)
            
            if response[1] != 200:
                return response

            return jsonify(response[0])
        except Exception as e:
            return {'message': str(e)}, 500
        
class UserPrs(Resource):
    @token_required()
    def get(self):
        try:
            current_user = g.current_user
            try:
                body = request.get_json()
            except Exception as e:
                body = {}
            
            start_date, end_date = get_date_range(body)

            github_user_resource = GitHubUser()
            response = github_user_resource.get_pr_stats(current_user.uid, start_date, end_date)
            
            if response[1] != 200:
                return response

            return jsonify(response[0])
        except Exception as e:
            return {'message': str(e)}, 500

class UserIssues(Resource):
    @token_required()
    def get(self):
        try:
            current_user = g.current_user
            try:
                body = request.get_json()
            except Exception as e:
                body = {}
            
            start_date, end_date = get_date_range(body)

            github_user_resource = GitHubUser()
            response = github_user_resource.get_issue_stats(current_user.uid, start_date, end_date)
            
            if response[1] != 200:
                return response

            return jsonify(response[0])
        except Exception as e:
            return {'message': str(e)}, 500

class UserIssueComments(Resource):
    @token_required()
    def get(self):
        try:
            current_user = g.current_user
            try:
                body = request.get_json()
            except Exception as e:
                body = {}
            
            start_date, end_date = get_date_range(body)

            github_user_resource = GitHubUser()
            response = github_user_resource.get_issue_comment_stats(current_user.uid, start_date, end_date)
            
            if response[1] != 200:
                return response

            return jsonify(response[0])
        except Exception as e:
            return {'message': str(e)}, 500

class UserReceivedIssueComments(Resource):
    def get(self):
        try:
            current_user = g.current_user
            try:
                body = request.get_json()
            except Exception as e:
                body = {}
            
            start_date, end_date = get_date_range(body)

            github_user_resource = GitHubUser()
            response = github_user_resource.get_total_received_issue_comments(current_user.uid, start_date, end_date)
            
            if response[1] != 200:
                return response

            return jsonify(response[0])
        except Exception as e:
            return {'message': str(e)}, 500

class GitHubOrgUsers(Resource):
    def get(self, org_name):
        try:
            github_org_resource = GitHubOrg()
            response = github_org_resource.get_users(org_name)
            
            if response[1] != 200:
                return response

            return jsonify(response[0])
        except Exception as e:
            return {'message': str(e)}, 500

class GitHubOrgRepos(Resource):
    def get(self, org_name):
        try:
            github_org_resource = GitHubOrg()
            response = github_org_resource.get_repos(org_name)
            
            if response[1] != 200:
                return response

            return jsonify(response[0])
        except Exception as e:
            return {'message': str(e)}, 500
        
class AdminUserIssues(Resource):
    def post(self, uid):
        try:
            # Check if the current user is an Admin
            if current_user.role != 'Admin':
                return {'message': 'Access denied: Admins only.'}, 403

            # Fetch the request body to extract date range (if any)
            try:
                body = request.get_json()
            except Exception as e:
                body = {}

            start_date, end_date = get_date_range(body)

            # Fetch the user based on uid
            user = User.query.filter_by(_uid=uid).first()

            if not user:
                return {'message': 'User not found'}, 404

            # Fetch submitted issue data for the specific user
            github_user_resource = GitHubUser()
            response = github_user_resource.get_issue_stats(user.uid, start_date, end_date)

            # Check if response is None or doesn't have the expected structure
            if response is None or len(response) < 2:
                return {'message': 'Error fetching issues for this user'}, 500

            return jsonify({
                'uid': user.uid,
                'issues': response[0]
            })

        except Exception as e:
            return {'message': str(e)}, 500



class AdminUserCommits(Resource):
    def post(self, uid):
        try:
            # Ensure the current user is an Admin
            if current_user.role != 'Admin':
                return {'message': 'Access denied: Admins only.'}, 403

            # Parse request body to extract date range (if any)
            try:
                body = request.get_json()
            except Exception as e:
                body = {}

            # Extract the start and end date
            start_date, end_date = get_date_range(body)

            # Fetch the user based on the provided UID
            user = User.query.filter_by(_uid=uid).first()

            if not user:
                return {'message': 'User not found'}, 404

            # Fetch commit data for the user from GitHub
            github_user_resource = GitHubUser()
            response = github_user_resource.get_commit_stats(user.uid, start_date, end_date)

            # If the response is invalid, handle it
            if response is None or len(response) < 2:
                return {'message': 'Error fetching commits for this user'}, 500

            return jsonify({
                'uid': user.uid,
                'commits': response[0]
            })

        except Exception as e:
            # Handle all other exceptions
            return {'message': str(e)}, 500

    def check_rate_limit(self, response):
        """Check if the rate limit is exceeded based on response headers"""
        remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
        reset_time = int(response.headers.get('X-RateLimit-Reset', time.time()))
        if remaining == 0:
            # If no requests remaining, calculate the time to wait
            wait_time = reset_time - time.time()
            print(f"Rate limit exceeded. Waiting for {wait_time} seconds.")
            time.sleep(wait_time + 5)  # Adding a buffer time to avoid immediate retry
            return True
        return False

    def retry_request(self, user_uid, start_date, end_date, retries=3):
        """Retry the request in case of rate limiting or server error"""
        attempt = 0
        while attempt < retries:
            try:
                github_user_resource = GitHubUser()
                response = github_user_resource.get_commit_stats(user_uid, start_date, end_date)

                if response.status_code == 500:
                    # Server error - retry after some delay
                    print(f"Attempt {attempt + 1}: Server error, retrying...")
                    time.sleep(5 * (2 ** attempt))  # Exponential backoff
                elif response.status_code == 403:
                    if self.check_rate_limit(response):
                        # Retry after rate limit reset
                        return self.retry_request(user_uid, start_date, end_date)
                else:
                    return response.json()  # Successfully processed the request
            except Exception as e:
                print(f"Error occurred: {e}")
            attempt += 1
        return None  # If retries are exhausted



api.add_resource(GitHubUserAPI, '/github/user')
api.add_resource(UserProfileLinks, '/github/user/profile_links')
api.add_resource(UserCommits, '/github/user/commits')
api.add_resource(UserPrs, '/github/user/prs')
api.add_resource(UserIssues, '/github/user/issues')
api.add_resource(UserIssueComments, '/github/user/issue_comments')
api.add_resource(UserReceivedIssueComments, '/github/user/received_issue_comments')
api.add_resource(GitHubOrgUsers, '/github/org/<string:org_name>/users')
api.add_resource(GitHubOrgRepos, '/github/org/<string:org_name>/repos')
api.add_resource(AdminUserCommits, '/commits/<string:uid>')  # Admin endpoint for commits
api.add_resource(AdminUserIssues, '/issues/<string:uid>')  # Admin endpoint for issues
