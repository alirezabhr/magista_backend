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


def remove_extra_posts_dirs(instagram_username, *dirs):
    """remove extra posts directory and directory contents in media root for an instagram online shop"""
    try:
        remove_shop_media_directory(instagram_username, *dirs)
    except OSError as e:
        print(f"Error: {e.filename} - {e.strerror}.")


def remove_extra_posts_dirs_and_images(extra_posts):
    """remove extra posts directory and images in media root for an instagram online shop"""

    removed_parents_id = []
    for extra_post in extra_posts[::-1]:  # reverse it because it's like stack, and want to pop
        if not extra_post.get('parent'):
            # it doesn't have parent so it is parent post
            pid = extra_post.get('id')
            remove_extra_posts_dirs(pid)
            removed_parents_id.append(pid)
        else:
            # it's child post
            if extra_post.get('parent') not in removed_parents_id:
                # its parent post was not removed
                remove_extra_posts_dirs(extra_post.get('parent'), extra_post.get('id'))


def remove_extra_posts_media_query(media_query_data, extra_posts):
    """remove extra posts data from media query json file of an instagram page"""

    data = media_query_data.copy()

    for extra_post in extra_posts[::-1]:
        """it should be reversed because extra_posts list is like stack,
        and it is possible to remove a parent before removing its child when it is reversed.
        So complexity will be reduced and function finished faster"""
        if not extra_post.get('parent'):
            # it was a parent post
            for mq in data:
                if mq['id'] == extra_post['id']:
                    data.remove(mq)
                    break
        else:
            # it was a child post
            for parent in data:
                if parent['id'] == extra_post['parent']:
                    for child in parent['children']:
                        if child['id'] == extra_post['id']:
                            parent['children'].remove(child)
                            break
                    break

    return data
