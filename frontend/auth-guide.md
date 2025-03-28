# Authentication Guide for Ollama Workshop Platform

This guide will help you test and use the authentication system in the Ollama Workshop Platform.

## Default Users

The system comes with two default users:

1. **Admin User**
   - Email: `admin@example.com`
   - Password: `admin`
   - Role: Administrator

2. **Regular User**
   - Email: `user@example.com`
   - Password: `password`
   - Role: Regular user

## Testing Authentication

### Using the API Directly

You can test authentication with curl:

```bash
# Get a token
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=admin"

# Sample response:
# {
#   "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#   "token_type": "bearer",
#   "user": {
#     "email": "admin@example.com",
#     "username": "admin",
#     "full_name": "Workshop Admin",
#     "disabled": false,
#     "is_admin": true
#   }
# }

# Use the token to access a protected endpoint
curl -X GET "http://localhost:8000/api/prompts" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Using the Frontend

1. Navigate to the login page
2. Enter the credentials for one of the default users
3. After successful login, the token will be stored in browser storage
4. You should now be able to access protected resources

## Debugging Authentication Issues

If you're experiencing authentication problems:

1. Check the network requests in your browser's developer tools
2. Ensure the Authorization header is being sent with requests
3. Verify the token hasn't expired
4. Use the debug endpoint to check your request headers:
   ```
   GET http://localhost:8000/api/public/auth-debug
   ```

## Creating New Users (Admin Only)

Only administrators can create new users:

```bash
# Create a new user (requires admin token)
curl -X POST "http://localhost:8000/api/users/register" \
  -H "Authorization: Bearer ADMIN_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "username": "newuser",
    "full_name": "New User",
    "password": "securepassword"
  }'
```

## Security Notes

For production use:
1. Change the default SECRET_KEY in the backend
2. Use HTTPS for all communication
3. Implement proper password policies
4. Consider adding rate limiting for login attempts
