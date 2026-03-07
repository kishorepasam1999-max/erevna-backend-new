from functools import wraps
from flask import request
from utils.exceptions import APIError

def validate(schema):
    def wrapper(fn):
        @wraps(fn)
        def decorated(*args, **kwargs):
            json = request.get_json()
            for field, ftype in schema.items():
                if field not in json:
                    raise APIError(f"Missing field: {field}")
                if not isinstance(json[field], ftype):
                    raise APIError(f"Invalid type for {field}")
            return fn(*args, **kwargs)
        return decorated
    return wrapper
