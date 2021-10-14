from datetime import datetime


def is_expired_otp(otp_date_time):
    now = datetime.utcnow()
    otp_time = otp_date_time.replace(tzinfo=None)
    diff = now - otp_time

    if diff.seconds > 300:  # if otp has been sent more than 5 minutes ago
        return False
    else:
        return True
