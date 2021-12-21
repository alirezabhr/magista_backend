import os
import shutil
from datetime import datetime

from django.conf import settings


def is_expired_otp(otp_date_time):
    now = datetime.utcnow()
    otp_time = otp_date_time.replace(tzinfo=None)
    diff = now - otp_time

    if diff.seconds > 300:  # if otp has been sent more than 5 minutes ago
        return False
    else:
        return True


def remove_shop_media_directory(ig_username, *dirs):
    dirs_path = ''
    for d in dirs:
        dirs_path = os.path.join(dirs_path, d)
    folder_path = os.path.join(settings.MEDIA_ROOT, 'shop', ig_username, dirs_path)

    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
