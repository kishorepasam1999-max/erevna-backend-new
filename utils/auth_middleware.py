from flask_jwt_extended import verify_jwt_in_request, get_jwt
from functools import wraps
from utils.exceptions import APIError

def require_role(*roles):
    def wrapper(fn):
        @wraps(fn)
        def decorated(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            role = claims.get("role")
            if role not in roles:
                raise APIError("Unauthorized", 403)
            return fn(*args, **kwargs)
        return decorated
    return wrapper
