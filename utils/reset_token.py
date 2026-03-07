import jwt
from datetime import datetime, timedelta

SECRET_KEY = "super-secret-key"  # change this


def create_reset_token(user_id):
    return jwt.encode(
        {
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(minutes=10)
        },
        SECRET_KEY,
        algorithm="HS256"
    )


def decode_reset_token(token):
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return data["user_id"]
    except:
        return None
