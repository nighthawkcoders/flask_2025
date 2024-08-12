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
    def update_ug_logic(config, uid, new_group):
        '''Utility method to update a KASM user'''
        SERVER, API_KEY, API_KEY_SECRET = config  # Unpack the configuration variables

        try:
            # find previous group and remove it via get user details
            response, error = KasmUtils.get_user_details(config, uid)
            if error:
                return None, error
            
            groups = response.json()['user']['groups']
            for group in groups:
                if 'group_id' in group:
                    current_group = group['group_id']
                    break

            # If the user is already in the target group, return
            if current_group == new_group:
                return None, {'message': 'User is already in the target group', 'code': 200}
            
            # Kasm API to update a user
            url = SERVER + "/api/public/add_user_group"  # Define the API endpoint URL

            # Prepare the data to be sent in the POST request
            data = {
                "api_key":API_KEY, # API key for authentication
                "api_key_secret": API_KEY_SECRET, # API key secret for authentication
                "target_user": {
                    "user_id": uid
                },
                "target_group": {
                    "group_id": new_group
                }
            }

            # Send a POST request to the Kasm server to update the user
            response = requests.post(url, json=data)

            # Check the status code of the response
            if response.status_code != 200:
                return None, response  # If the status code is not 200, return None and the response

        # Handle any exceptions that occur during the request
        except requests.RequestException as e:
            # Return None and an error message if the request fails
            return None, {'message': 'Failed to update user', 'code': 500, 'error': str(e)}
        
class UpdateUser:
    def group_change(uid, new_group):
        '''
        Interface to update a KASM user group
        Why this method does not fail? Even if the user is not found or not updated.
        This method does not fail as Kasm is a complementary and 3rd party service. 
        If failure occurs, admin or user will try again.
        
        uid: User ID to update
        new_group: New group name
        '''
        
        config, error = KasmUtils.get_config()
        if error:
            print(error)
            return
        if config is None:
            print("Configuration is missing")
            return
        
        # Check if KASM keys can authenticate, the "_" means data is not used
        _, error = KasmUtils.authenticate(config)
        if error:
            print(error)
            return
        
        # Extract all KASM users
        users, error = KasmUtils.get_users(config)
        if error:
            print(error)
            return
        
        # find the requested user_id, and get all the info out of it ie the last name, first name, password, all of it
        kasm_user_id = KasmUtils.get_user_id(users, uid)
        if kasm_user_id is None:
            print({'message': f'Kasm user {uid} not found for update', 'code': 404})
            return
        
        # update users group
        response, error = KasmUtils.update_ug_logic(config, kasm_user_id, new_group)
        if error:
            print(error)
            return


        return response

class KasmUser:
    def post(self, name, uid, password):
        '''
        Interface to create a KASM user
        Why this method does not fail? Even if the user is created.
        This method does not fail as Kasm is a complementary and 3rd party service. 
        If failure occurs, admin or user will try again.
        
        uid: User ID to delete
        username: Should be set to username for all use cases, the changes between uid and username are getting confusing.
        '''
        
        # Get KASM keys
        config, error = KasmUtils.get_config()
        if error:
            # print(error)
            return

        # Check if KASM keys can authenticate, the "_" means data is not used
        _, error = KasmUtils.authenticate(config)
        if error:
            print(error)
            return

        # Prepare data for KASM user creation
        full_name = name
        words = full_name.split()

        if len(words) > 1:
            first_name = " ".join(words[:-1])  # Join all but the last word for first name
            last_name = words[-1]  # Last word is the last name
        else:
            first_name = words[0]  # Only word is the first name
            last_name = ""  # No last name

        # Check if password is provided
        if password is None:
            print({'message': 'Password is required', 'code': 400})
            return 
        
        # Attempt to create a KASM user
        response, error = KasmUtils.create_user(config, uid, first_name, last_name, password)
        if error:
            print(error)
            return
        
        # Debugging output 
        print(response)

        # print info about user from response, find uid provided from kasm
        print(response.json())

    def delete(self, uid):
        '''
        Interface to delete a KASM user.
        Why this method does not fail? Even if the user is not found or not deleted.
        This method does not fail as Kasm is a complementary and 3rd party service. 
        If failure occurs, admin or user will try again.
        
        uid: User ID to delete
        '''
        
        # Get KASM keys
        config, error = KasmUtils.get_config()
        if error:
            # print(error)
            return

        # Check if KASM keys can authenticate, the "_" means data is not used
        _, error = KasmUtils.authenticate(config)
        if error:
            print(error)
            return
        
        # Extract all KASM users
        users, error = KasmUtils.get_users(config)
        if error:
            print(error)
            return
        
        # Find the requested user_id, Kasm reference number to uid
        kasm_user_id = KasmUtils.get_user_id(users, uid)
        if kasm_user_id is None:
            print({'message': f'Kasm user {uid} not found for delete', 'code': 404})
            return

        # Attempt to delete the user
        response, error = KasmUtils.delete_user(config, kasm_user_id)
        if error:
            print(error)
            return

        # Debugging output
        print(response)