import requests
from __init__ import app

class KasmUtils:
    @staticmethod
    def get_config():
        '''Utility method to get KASM keys'''
        SERVER = app.config.get('KASM_SERVER')
        API_KEY = app.config.get('KASM_API_KEY')
        API_KEY_SECRET = app.config.get('KASM_API_KEY_SECRET')
        if not SERVER or not API_KEY or not API_KEY_SECRET:
            return None, {'message': '1 or more KASM keys are missing to create a user', 'code': 400}
        return (SERVER, API_KEY, API_KEY_SECRET), None

    @staticmethod
    def authenticate(config):
        '''Utility method to authenticate KASM keys''' 
        SERVER, API_KEY, API_KEY_SECRET = config
        try:
            url = SERVER + "/api/public/validate_credentials"
            data = {
                "api_key": API_KEY,
                "api_key_secret": API_KEY_SECRET
            }
            response = requests.post(url, json=data)
            if response.status_code != 200:
                return None, response
        except requests.RequestException as e:
            return None, {'message': 'Failed to authenticate', 'code': 500, 'error': str(e)}
        return response, None
    
    @staticmethod
    def get_authenticated_config():
        '''Utility method to combine get_config and authenticate''' 
        config, error = KasmUtils.get_config()
        if error:
            return None, error

        _, error = KasmUtils.authenticate(config)
        if error:
            return None, error

        # Return KASM API keys
        return config, None


    @staticmethod
    def get_user_id(users, uid):
        '''Find the requested uid in the list Kasm users'''
        for user in users:
            # Kasm username maps to uid from the request
            if user['username'].lower() == uid.lower():
                # kasm user_id is the reference number for the user
                return user['user_id']
        return None

    @staticmethod
    def get_users(config):
        '''Utility method to get all KASM users'''
        SERVER, API_KEY, API_KEY_SECRET = config
        try:
            # Kasm API to get all users
            url = SERVER + "/api/public/get_users"
            data = {
                "api_key": API_KEY,
                "api_key_secret": API_KEY_SECRET
            }
            response = requests.post(url, json=data)
            if response.status_code != 200:
                return None, {'message': 'Failed to get users', 'code': response.status_code}

            users = response.json()['users']  # This should be your users list
        except:
            return None, {'message': 'Failed to get users', 'code': 500}
        return users, None
    
    @staticmethod
    def get_kasm_user_id(config, uid):
        '''Utility method to combine get_users and get_user_id'''
        # Extract all KASM users
        users, error = KasmUtils.get_users(config)
        if error:
            return None, error
        
        # find the requested user_id
        user_id = KasmUtils.get_user_id(users, uid)
        if user_id is None:
            return None, {'message': f'Kasm user {uid} not found', 'code': 404}
       
        # Return KASM user_id, this is KASM internal reference number 
        return user_id, None
        
    
    @staticmethod
    def get_groups(config):
        '''Utility method to get all KASM groups'''
        SERVER, API_KEY, API_KEY_SECRET = config
        try:
            # Kasm API to get all groups
            url = SERVER + "/api/public/get_groups"
            data = {
                "api_key": API_KEY,
                "api_key_secret": API_KEY_SECRET
            }
            response = requests.post(url, json=data)
            if response.status_code != 200:
                return None, {'message': 'Failed to get groups', 'code': response.status_code}

            groups = response.json()['groups']  # This should be your groups list
        except:
            return None, {'message': 'Failed to get groups', 'code': 500}
        return groups, None
    
    @staticmethod
    def create_user(config, uid, first_name, last_name, password):
        '''Utility method to create a KASM user'''
        SERVER, API_KEY, API_KEY_SECRET = config
        try:
            # Kasm API to create a user
            url = SERVER + "/api/public/create_user"
            data = {
                "api_key": API_KEY,
                "api_key_secret": API_KEY_SECRET,
                "target_user": {
                    "username": uid,
                    "first_name": first_name,
                    "last_name": last_name,
                    "locked": False,
                    "disabled": False,
                    "organization": "All Users",
                    "phone": "123-456-7890",
                    "password": password,
                }
            }
            response = requests.post(url, json=data)
            if response.status_code != 200:
                return None, response
             
        except requests.RequestException as e:
            return None, {'message': 'Failed to create user', 'code': 500, 'error': str(e)}
        
        return response, None
    
    @staticmethod
    def update_user_password(config, user_id, new_password):
        '''Utility method to update a KASM user's password'''
        SERVER, API_KEY, API_KEY_SECRET = config
        try:
            # Kasm API to update a user password
            url = SERVER + "/api/public/update_user_password"
            data = {
                "api_key": API_KEY,
                "api_key_secret": API_KEY_SECRET,
                "target_user": {
                    "user_id": user_id,
                    "password": new_password
                }
            }
            response = requests.post(url, json=data)
            if response.status_code != 200:
                return None, response
        except requests.RequestException as e:
            return None, {'message': 'Failed to update password', 'code': 500, 'error': str(e)}
        return response, None
    
    
    
    @staticmethod
    def update_user_name(config, user_id, first_name, last_name):
        '''Utility method to update a KASM user's name'''
        SERVER, API_KEY, API_KEY_SECRET = config
        try:
            # Kasm API to update a user name
            url = SERVER + "/api/public/update_user_name"
            data = {
                "api_key": API_KEY,
                "api_key_secret": API_KEY_SECRET,
                "target_user": {
                    "user_id": user_id,
                    "first_name": first_name,
                    "last_name": last_name
                }
            }
            response = requests.post(url, json=data)
            if response.status_code != 200:
                return None, response
        except requests.RequestException as e:
            return None, {'message': 'Failed to update name', 'code': 500, 'error': str(e)}
        return response, None


        
    @staticmethod
    def get_user_details(config, user_id):
        '''Utility method to get a KASM user details'''
        SERVER, API_KEY, API_KEY_SECRET = config
        try:
            # Kasm API to get a user
            url = SERVER + "/api/public/get_user"
            data = {
                "api_key": API_KEY,
                "api_key_secret": API_KEY_SECRET,
                "target_user": {
                    "user_id": user_id
                }
            }
            response = requests.post(url, json=data)
            if response.status_code != 200:
                return None, response
        except requests.RequestException as e:
            return None, {'message': 'Failed to get user details', 'code': 500, 'error': str(e)}
        
        return response, None
            
    @staticmethod
    def delete_user(config, user_id):
        '''Utility method to delete a KASM user'''
        SERVER, API_KEY, API_KEY_SECRET = config
        try:
            # Kasm API to delete a user
            url = SERVER + "/api/public/delete_user"
            data = {
                "api_key": API_KEY,
                "api_key_secret": API_KEY_SECRET,
                "target_user": {
                    "user_id": user_id
                },
                "force": False
            }
            response = requests.post(url, json=data)
            if response.status_code != 200:
                return None, response 
            
        except requests.RequestException as e:
            return None, {'message': 'Failed to delete user', 'code': 500, 'error': str(e)}
        
        return response, None
    
    @staticmethod
    def update_user_group(config, user_id, new_group):
        '''Utility method to update a KASM user'''
        SERVER, API_KEY, API_KEY_SECRET = config  # Unpack the configuration variables

        try:
            # find previous group and remove it via get user details
            response, error = KasmUtils.get_user_details(config, user_id)
            if error:
                return None, error
           
            # Check if the user is already in the target group 
            user_groups = response.json()['user']['groups']
            for group in user_groups:
                if 'name' in group:
                    if group['group_id'] == new_group:
                        return None, {'message': 'User is already in the target group', 'code': 200}
                        break
            
            # Check if the target group exists        
            all_groups, error = KasmUtils.get_groups(config)
            group_id = None
            for group in all_groups:
                if group['name'] == new_group:
                    group_id = group['group_id']
                    break
            
            # Abort if the group does not exist 
            if group_id is None:
                return None, {'message': 'Group not found', 'code': 404}     
                    
            # Kasm API to update a user
            url = SERVER + "/api/public/add_user_group"  # Define the API endpoint URL

            # Prepare the data to be sent in the POST request
            data = {
                "api_key": API_KEY, # API key for authentication
                "api_key_secret": API_KEY_SECRET, # API key secret for authentication
                "target_user": {
                    "user_id": user_id 
                },
                "target_group": {
                    "group_id": group_id
                }
            }

            # Send a POST request to the Kasm server to update the user
            response = requests.post(url, json=data)

            # Check the status code of the response
            if response.status_code != 200:
                return None, response  # If the status code is not 200, return None and the response
            
            return response, None  # If the status code is 200, return the response and None

        # Handle any exceptions that occur during the request
        except requests.RequestException as e:
            # Return None and an error message if the request fails
            return None, {'message': 'Failed to update user', 'code': 500, 'error': str(e)}
        
class KasmUser:
    def post(self, name, uid, password):
        '''
        Refactored method to check if a user exists in KASM, update details if they do,
        or create a new user if they don't exist.
        
        uid: User ID to check
        name: Full name of the user (first and last names)
        password: User's password (required for creation, optional for updates)
        '''

        # Get KASM API keys 
        config, error = KasmUtils.get_authenticated_config()
        if error:
            print(error)
            return
        
        # Kept first and last name code
        full_name = name
        words = full_name.split()
        if len(words) > 1:
            first_name = " ".join(words[:-1])
            last_name = words[-1]
        else:
            first_name = words[0]
            last_name = ""
        
        # Check if the user exists in KASM with  get_kasm_user_id
        kasm_user_id, error = KasmUtils.get_kasm_user_id(config, uid)
        
        if kasm_user_id:
            # User exists, check for updates
            print(f"User with UID {uid} exists. Proceeding with updates...")

            # Update password if provided
            if password:
                response, error = KasmUtils.update_user_password(config, kasm_user_id, password)
                if error:
                    print(f"Failed to update password: {error}")
                else:
                    print(f"Password updated for user {uid}: {response}")
            
            # Write method to update name 
            current_user_info, error = KasmUtils.get_user_details(config, kasm_user_id)
            if current_user_info:
                current_first_name = current_user_info.get("first_name")
                current_last_name = current_user_info.get("last_name")
                
                if current_first_name != first_name or current_last_name != last_name:
                    response, error = KasmUtils.update_user_name(config, kasm_user_id, first_name, last_name)
                    if error:
                        print(f"Failed to update name: {error}")
                    else:
                        print(f"Name updated for user {uid}: {response}")
            else:
                print(f"Failed to retrieve user information: {error}")
        
        else:
            # User does not exist, create a new one
            print(f"User with UID {uid} does not exist. Creating a new user...")

            # Ensure password is provided
            if not password:
                print({'message': 'Password is required for new user creation', 'code': 400})
                return
            
            # Attempt to create the user
            response, error = KasmUtils.create_user(config, uid, first_name, last_name, password)
            if error:
                print(f"Failed to create user: {error}")
            else:
                print(f"User {uid} created: {response}")

        
    def post_groups(self, uid, groups):
        '''
        Interface to update a KASM user groups
        Why this method does not throw exception? Even if the user is not found or not updated.
        This method does not fail as Kasm is a complementary and 3rd party service. 
        If failure occurs, admin or user will be required to try again.
        
        uid: User ID to update
        groups: List of groups to add to user
        '''
       
        # Get KASM API keys 
        config, error = KasmUtils.get_authenticated_config()
        if error:
            print(error)
            return
        
        # Get KASM user_id
        kasm_user_id, error = KasmUtils.get_kasm_user_id(config, uid)
        if kasm_user_id is None:
            print(error)
            return
        
        # update user groups
        for group in groups:
            response, error = KasmUtils.update_user_group(config, kasm_user_id, group)
            if error:
              print(error)
              continue
            print(response)
            

    def delete(self, uid):
        '''
        Interface to delete a KASM user.
        Why this method does not throw exception? Even if the user is not found or not deleted.
        This method does not fail as Kasm is a complementary and 3rd party service. 
        If failure occurs, admin or user will be required to try again.
        
        uid: User ID to delete
        '''
        
        # Get KASM API keys 
        config, error = KasmUtils.get_authenticated_config()
        if error:
            print(error)
            return
        
        # Get KASM user_id
        kasm_user_id, error = KasmUtils.get_kasm_user_id(config, uid)
        if kasm_user_id is None:
            print(error)
            return 

        # Attempt to delete the user
        response, error = KasmUtils.delete_user(config, kasm_user_id)
        if error:
            print(error)
            return

        # Debugging output
        print(response)