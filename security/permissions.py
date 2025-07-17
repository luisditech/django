import jwt
from datetime import datetime, timezone
from functools import wraps
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.response import Response
from django.conf import settings

def has_permission(user, required_permission):
    if not user.is_authenticated or not user.role:
        print('false')
        return False

    permissions_by_role = {
        "admin": {"view_users", "view_connections", "access_dashboard", "edit_pending_users", 'read_pending_users'},
        "manager": { 'read_pending_users' },
        "operator": {"view_connections"},
        "example_custom_app": {"access_dashboard"},
    }

    role_name = getattr(user.role, "name", "").lower()
    permissions = permissions_by_role.get(role_name, set())

    return required_permission in permissions

def requires_permission(permission):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(self, request, *args, **kwargs):
            print(request.user)
            if not has_permission(request.user, permission):
                return Response({"error": "Not authorized"}, status=403)
            return view_func(self, request, *args, **kwargs)
        return _wrapped_view
    return decorator

def check_token_and_recovery_code(view_func):
    @wraps(view_func)
    def _wrapped_view(self, request, *args, **kwargs):
        # Get the Authorization header
        auth_header = request.headers.get("Authorization")
        print(f"Authorization header: {auth_header}")  # Debugging print
        
        if not auth_header or not auth_header.startswith("Bearer "):
            return Response({"error": "Token missing or invalid"}, status=401)

        token = auth_header.split(" ")[1]
        
        # Get recovery code from the request body
        recovery_code = request.data.get("recovery_code")
        print(f"Recovery code from request: {recovery_code}")  # Debugging print

        try:
            # Decode the token using Simple JWT's AccessToken
            decoded_token = AccessToken(token)
            print(f"Decoded token: {decoded_token}")  # Debugging print

            # Check if the token is expired
            if decoded_token.exp < now().timestamp():
                return Response({"error": "Token expired"}, status=403)

            # Get the user ID and recovery code from the token
            user_id = decoded_token["user_id"]
            token_recovery_code = decoded_token.get("recovery_code")

            # Retrieve the user from the database using the user_id
            try:
                user = User.objects.get(id=user_id)  # Assuming you're using the default User model
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=404)

            # Check if the recovery code matches
            if token_recovery_code != recovery_code:
                return Response({"error": "Invalid recovery code"}, status=403)

        except InvalidToken:
            return Response({"error": "Invalid token"}, status=401)
        except TokenError:
            return Response({"error": "Error decoding token"}, status=401)

        # Proceed to the actual view function if all checks pass
        return view_func(self, request, *args, **kwargs)

    return _wrapped_view