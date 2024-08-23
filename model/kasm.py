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
            return None, {'message': '1 or more KASM keys are missing', 'code': 400}
        return (SERVER, API_KEY, API_KEY_SECRET), None

    @staticmethod
    def authenticate(config):
        '''Utility method to authenticate KASM keys''' 
        KASM_SERVER, KASM_API_KEY, API_KEY_SECRET = config
        try:
            url = KASM_SERVER + "/api/public/validate_credentials"
            headers = {
                "Authorization": f"Bearer {KASM_API_KEY}",  # Include the API key in the header if needed
                "Content-Type": "application/json"
            }
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                return None, {'message': 'Failed to authenticate', 'code': response.status_code}
        except requests.RequestException as e:
            return None, {'message': 'Failed to authenticate', 'code': 500, 'error': str(e)}
        return response, None


    @staticmethod
    def get_user_id(users, uid):
        '''Find the requested uid in the list of Kasm users'''
        for user in users:
            if user['username'].lower() == uid.lower():
                return user['user_id']
        return None

    @staticmethod
    def get_users(config):
        '''Utility method to get all KASM users'''
        SERVER, API_KEY, API_KEY_SECRET = config
        try:
            url = SERVER + "/api/public/get_users"
            data = {"api_key": API_KEY, "api_key_secret": API_KEY_SECRET}
            response = requests.post(url, json=data)
            if response.status_code != 200:
                return None, {'message': 'Failed to get users', 'code': response.status_code}
            return response.json().get('users', []), None
        except requests.RequestException as e:
            return None, {'message': 'Failed to get users', 'code': 500, 'error': str(e)}
    
    @staticmethod
    def get_groups(config):
        '''Utility method to get all KASM groups'''
        SERVER, API_KEY, API_KEY_SECRET = config
        try:
            url = SERVER + "/api/public/get_groups"
            data = {"api_key": API_KEY, "api_key_secret": API_KEY_SECRET}
            response = requests.post(url, json=data)
            if response.status_code != 200:
                return None, {'message': 'Failed to get groups', 'code': response.status_code}
            return response.json().get('groups', []), None
        except requests.RequestException as e:
            return None, {'message': 'Failed to get groups', 'code': 500, 'error': str(e)}
    
    @staticmethod
    def create_user(config, uid, first_name, last_name, password):
        '''Utility method to create a KASM user'''
        SERVER, API_KEY, API_KEY_SECRET = config
        try:
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
                return None, {'message': 'Failed to create user', 'code': response.status_code}
        except requests.RequestException as e:
            return None, {'message': 'Failed to create user', 'code': 500, 'error': str(e)}
        return response, None
    
    @staticmethod
    def get_user_details(config, user_id):
        '''Utility method to get a KASM user details'''
        SERVER, API_KEY, API_KEY_SECRET = config
        try:
            url = SERVER + "/api/public/get_user"
            data = {
                "api_key": API_KEY,
                "api_key_secret": API_KEY_SECRET,
                "target_user": {"user_id": user_id}
            }
            response = requests.post(url, json=data)
            if response.status_code != 200:
                return None, {'message': 'Failed to get user details', 'code': response.status_code}
        except requests.RequestException as e:
            return None, {'message': 'Failed to get user details', 'code': 500, 'error': str(e)}
        return response, None
            
    @staticmethod
    def delete_user(config, user_id):
        '''Utility method to delete a KASM user'''
        SERVER, API_KEY, API_KEY_SECRET = config
        try:
            url = SERVER + "/api/public/delete_user"
            data = {
                "api_key": API_KEY,
                "api_key_secret": API_KEY_SECRET,
                "target_user": {"user_id": user_id},
                "force": False
            }
            response = requests.post(url, json=data)
            if response.status_code != 200:
                return None, {'message': 'Failed to delete user', 'code': response.status_code}
        except requests.RequestException as e:
            return None, {'message': 'Failed to delete user', 'code': 500, 'error': str(e)}
        return response, None
    
    @staticmethod
    def update_user_group(config, user_id, new_group):
        '''Utility method to update a KASM user group'''
        SERVER, API_KEY, API_KEY_SECRET = config
        try:
            # Find previous group and remove it
            response, error = KasmUtils.get_user_details(config, user_id)
            if error:
                return None, error
           
            user_groups = response.json().get('user', {}).get('groups', [])
            if any(group.get('group_id') == new_group for group in user_groups):
                return None, {'message': 'User is already in the target group', 'code': 200}
            
            all_groups, error = KasmUtils.get_groups(config)
            if error:
                return None, error

            group_id = next((group['group_id'] for group in all_groups if group['name'] == new_group), None)
            if group_id is None:
                return None, {'message': 'Group not found', 'code': 404}
                    
            url = SERVER + "/api/public/add_user_group"
            data = {
                "api_key": API_KEY,
                "api_key_secret": API_KEY_SECRET,
                "target_user": {"user_id": user_id},
                "target_group": {"group_id": group_id}
            }
            response = requests.post(url, json=data)
            if response.status_code != 200:
                return None, {'message': 'Failed to update user group', 'code': response.status_code}
            return response, None
        except requests.RequestException as e:
            return None, {'message': 'Failed to update user group', 'code': 500, 'error': str(e)}
        
    @staticmethod
    def update_user_password(user_id, username, new_password):
        '''Utility method to update a KASM user's password'''
        SERVER = app.config.get('KASM_SERVER')
        API_KEY = app.config.get('KASM_API_KEY')
        API_KEY_SECRET = app.config.get('KASM_API_KEY_SECRET')

        try:
            url = SERVER + "/api/public/update_user"
            data = {
                "api_key": API_KEY,
                "api_key_secret": API_KEY_SECRET,
                "target_user": {
                    "user_id": user_id,
                    "username": username,   # Include the username
                    "password": new_password
                }
            }
            response = requests.post(url, json=data)

            # Log detailed request and response information for debugging
            print(f"Request URL: {url}")
            print(f"Request Data: {data}")
            print(f"Response Status Code: {response.status_code}")
            print(f"Response Text: {response.text}")

            if response.status_code != 200:
                return None, {
                    'message': f"Failed to update user password: {response.text}",
                    'code': response.status_code
                }
            return response.json(), None
        except requests.RequestException as e:
            return None, {
                'message': f"Failed to update user password due to a request exception: {str(e)}",
                'code': 500,
                'error': str(e)
            }
        
    @staticmethod
    def auth_test():
        config, error = KasmUtils.get_config()
        if error:
            print("Kasm config error")
            print(error)
            return
        
        _, error = KasmUtils.authenticate(config)
        if error:
            print("Kasm auth error")
            print(error)
            return
        
        return "auth success"
    

class KasmUser:
    def post(self, name, uid, password):
        '''
        Interface to create a KASM user.
        
        name: Full name of the user
        uid: User ID to create
        password: Password for the user
        '''
        config, error = KasmUtils.get_config()
        if error:
            print(error)
            return

        _, error = KasmUtils.authenticate(config)
        if error:
            print(error)
            return

        full_name = name
        words = full_name.split()
        first_name = " ".join(words[:-1]) if len(words) > 1 else ""
        last_name = words[-1]

        response, error = KasmUtils.create_user(config, uid, first_name, last_name, password)
        if error:
            print(error)
        else:
            print(response.json())

    def delete(self, uid):
        '''
        Interface to delete a KASM user.
        
        uid: User ID to delete
        '''
        config, error = KasmUtils.get_config()
        if error:
            print(error)
            return

        _, error = KasmUtils.authenticate(config)
        if error:
            print(error)
            return

        users, error = KasmUtils.get_users(config)
        if error:
            print(error)
            return

        user_id = KasmUtils.get_user_id(users, uid)
        if not user_id:
            print({'message': 'User not found', 'code': 404})
            return

        response, error = KasmUtils.delete_user(config, user_id)
        if error:
            print(error)
        else:
            print(response.json())

    def update_group(self, uid, new_group):
        '''
        Interface to update the group of a KASM user.
        
        uid: User ID to update
        new_group: Name of the new group
        '''
        config, error = KasmUtils.get_config()
        if error:
            print(error)
            return

        _, error = KasmUtils.authenticate(config)
        if error:
            print(error)
            return

        users, error = KasmUtils.get_users(config)
        if error:
            print(error)
            return

        user_id = KasmUtils.get_user_id(users, uid)
        if not user_id:
            print({'message': 'User not found', 'code': 404})
            return

        response, error = KasmUtils.update_user_group(config, user_id, new_group)
        if error:
            print(error)
        else:
            print(response.json())

    def update_password(self, username, new_password):
        '''
        Interface to update the password of a KASM user.
        
        uid: User ID to update
        new_password: New password
        '''
        #  1: Get the KASM configuration
        config, error = KasmUtils.get_config()
        if error:
            print("Kasm config error")
            print(error)
            return

    
        #  2: Retrieve all users
        users, error = KasmUtils.get_users(config)
        if error:
            print("Kasm user retrieval error")
            print(error)
            return

        #  3: Find the user ID
        user_id = KasmUtils.get_user_id(users, username)
        if not user_id:
            print({'message': 'User not found', 'code': 404})
            return

        #  4: Update the password
        response, error = KasmUtils.update_user_password(user_id, username, new_password)
        if error:
            print(error)
        else:
            print("Password change success!")
    
    
    def test_config(self):
        '''Utility function to test if the config values are accessed properly'''
        SERVER = app.config.get('KASM_SERVER')
        API_KEY = app.config.get('KASM_API_KEY')
        API_KEY_SECRET = app.config.get('KASM_API_KEY_SECRET')
        
        if not SERVER or not API_KEY or not API_KEY_SECRET:
            print("Configuration error: One or more KASM keys are missing")
            return
        
        # Print configuration details
        print("Configuration Details:")
        print(f"Server: {SERVER}")
        print(f"API Key: {API_KEY}")
        print(f"API Key Secret: {API_KEY_SECRET}")
        
        return SERVER, API_KEY, API_KEY_SECRET
