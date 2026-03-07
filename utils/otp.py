import random
import datetime

class OTP:
    @staticmethod
    def generate():
        otp = random.randint(100000, 999999)   # 6 digit OTP
        expiry = datetime.datetime.now() + datetime.timedelta(minutes=5)
        return str(otp), expiry

    @staticmethod
    def is_expired(expiry_time):
        return datetime.datetime.now() > expiry_time
