import re
from functools import wraps
from rest_framework.response import Response

def check_password_security(view_func):
    @wraps(view_func)
    def _wrapped_view(self, request, *args, **kwargs):
        password = request.data.get("password")
        errors = []

        if not password:
            return Response({"errors": ["Password is required"]}, status=400)

        if len(password) < 8:
            errors.append("Password must be at least 10 characters long")

        if not re.search(r"[A-Z]", password):
            errors.append("Password must contain at least one uppercase letter")

        if not re.search(r"[a-z]", password):
            errors.append("Password must contain at least one lowercase letter")

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            errors.append("Password must contain at least one special character")

        if errors:
            return Response({"errors": errors}, status=400)

        return view_func(self, request, *args, **kwargs)

    return _wrapped_view