# KASM User Update Documentation

## Overview

This documentation provides a detailed guide on how to update a user in KASM using the KASM API. It covers the API endpoint, the required data structure, and the process to follow. Additionally, it highlights the password requirements enforced by KASM.

## API Endpoint

To update a user in KASM, use the following endpoint:

```
POST /api/public/update_user
```

### Request Structure

The request to update a user should include the following JSON payload:

```json
{
  "api_key": "YOUR_API_KEY",
  "api_key_secret": "YOUR_API_KEY_SECRET",
  "target_user": {
    "user_id": "USER_ID",
    "username": "NEW_USERNAME",
    "first_name": "NEW_FIRST_NAME",
    "last_name": "NEW_LAST_NAME",
    "locked": false,
    "disabled": false,
    "organization": "NEW_ORGANIZATION",
    "phone": "123-456-7890",
    "password": "NEW_PASSWORD"
  }
}
```

- **api_key**: Your KASM API key.
- **api_key_secret**: The secret associated with your KASM API key.
- **user_id**: The unique identifier of the user to update.
- **username**: (Optional) The new username for the user.
- **first_name**: (Optional) The new first name of the user.
- **last_name**: (Optional) The new last name of the user.
- **locked**: (Optional) Boolean value indicating whether the user's account is locked.
- **disabled**: (Optional) Boolean value indicating whether the user's account is disabled.
- **organization**: (Optional) The new organization or group to which the user belongs.
- **phone**: (Optional) The phone number of the user.
- **password**: (Optional) The new password for the user.

### Password Requirements

KASM enforces strong password requirements to ensure user account security. The password must meet the following criteria:

- At least 8 characters long
- Includes at least one uppercase letter
- Includes at least one lowercase letter
- Includes at least one number
- Includes at least one special character (e.g., !, @, #, $, etc.)

### Example Request

Here is an example of an update request:

```json
{
  "api_key": "example_api_key",
  "api_key_secret": "example_api_key_secret",
  "target_user": {
    "user_id": "1234",
    "username": "new_username",
    "first_name": "New",
    "last_name": "User",
    "locked": false,
    "disabled": false,
    "organization": "New Organization",
    "phone": "123-456-7890",
    "password": "NewP@ssw0rd"
  }
}
```

### Response

A successful request will return a 200 status code along with the updated user details in the response body. If the request fails, the API will return an error message and a corresponding status code.

## Error Handling

If the user update fails, the KASM API will return an error message. Common reasons for failure include:

- **Invalid API credentials**: Ensure that the `api_key` and `api_key_secret` are correct.
- **User not found**: The `user_id` provided does not match any existing users.
- **Password does not meet requirements**: Ensure that the new password complies with KASM's security policies.