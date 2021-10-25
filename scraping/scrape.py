import requests
import json
import hashlib
import sys

import os
from django.conf import settings

from .constants import *


def logger(message):
    print('----------\n')
    print(message)
    print('\n----------')


class CustomException(Exception):
    def __init__(self, status, message):
        self.status = status
        self.message = message


class Scraper:
    def __init__(self, login_user=None, login_pass=None) -> None:
        self.username = login_user
        self.password = login_pass

        self.session = requests.Session()
        self.session.headers = {'user-agent': CHROME_WIN_UA}
        self.session.cookies.set('ig_pr', '1')
        self.rhx_gis = ""

        self.cookies = None
        self.login = False
        self.authenticated = False
        self.logged_in = False

    def authenticate_with_login(self):
        """Logs in to instagram."""
        self.session.headers.update({'Referer': BASE_URL, 'user-agent': STORIES_UA})
        req = self.session.get(BASE_URL)

        self.session.headers.update({'X-CSRFToken': req.cookies['csrftoken']})

        login_data = {'username': self.username, 'password': self.password}
        login = self.session.post(LOGIN_URL, data=login_data, allow_redirects=True)
        self.session.headers.update({'X-CSRFToken': login.cookies['csrftoken']})
        self.cookies = login.cookies
        login_text = json.loads(login.text)

        if login_text.get('authenticated') and login.status_code == 200:
            self.authenticated = True
            self.logged_in = True
            self.session.headers.update({'user-agent': CHROME_WIN_UA})
            self.rhx_gis = ""
        else:
            logger('Login failed for ' + self.username)
            raise CustomException(500, 'Login failed')

    def logout(self):
        """Logs out of instagram."""
        if self.logged_in:
            try:
                logout_data = {'csrfmiddlewaretoken': self.cookies['csrftoken']}
                self.session.post(LOGOUT_URL, data=logout_data)
                self.authenticated = False
                self.logged_in = False
            except requests.exceptions.RequestException:
                logger('Failed to log out ' + self.username)

    def get_data(self, url):
        response = self.session.get(url=url, timeout=CONNECT_TIMEOUT, cookies=self.cookies)
        if response.status_code == 200:
            return response.text
        elif response.status_code == 404:
            logger('page not found')
            raise CustomException(404, "پیج مورد نظر یافت نشد.")
        else:
            logger('something bad happened in get_data function')
            error_data = {
                'status_code': response.status_code,
                'text': response.text
            }
            raise CustomException(500, error_data)

    def query_media_gen(self, user_id, end_cursor=''):
        """Generator for media."""
        media, end_cursor = self.__query_media(user_id, end_cursor)

        if media:
            try:
                while True:
                    for item in media:
                        # if not self.is_new_media(item):
                        #     return
                        yield item

                    if end_cursor:
                        media, end_cursor = self.__query_media(user_id, end_cursor)
                    else:
                        return
            except ValueError:
                logger('Failed to query media for user ' + user_id)
                raise CustomException(500, 'Failed to query media for user ' + user_id)

    def __query_media(self, ig_id, end_cursor=''):
        params = QUERY_MEDIA_VARS.format(ig_id, end_cursor)
        self.update_ig_gis_header(params)

        resp = self.get_data(QUERY_MEDIA.format(params))

        if resp is not None:
            payload = json.loads(resp)['data']['user']
            if payload:
                container = payload['edge_owner_to_timeline_media']
                nodes = self._get_nodes(container)
                end_cursor = container['page_info']['end_cursor']
                return nodes, end_cursor

        return None, None

    def get_ig_gis(self, rhx_gis, params):
        data = rhx_gis + ":" + params
        if sys.version_info.major >= 3:
            return hashlib.md5(data.encode('utf-8')).hexdigest()
        else:
            return hashlib.md5(data).hexdigest()

    def update_ig_gis_header(self, params):
        self.session.headers.update({
            'x-instagram-gis': self.get_ig_gis(
                self.rhx_gis,
                params
            )
        })

    def _get_nodes(self, container):
        return [node['node'] for node in container['edges']]
        # return [self.__change_node(node['node']) for node in container['edges']]

    def __change_node(self, node):
        new_node = {
            "id": node['id'],
            "__typename": node['__typename'],
            "caption": node['edge_media_to_caption']['edges'][0]['node']['text'],
            "shortcode": node['shortcode'],
            "display_url": node['display_url'],
            "thumbnail_src": node['thumbnail_src'],
            "thumbnail_resources": node['thumbnail_resources'],
            "is_video": node['is_video']
        }
        return new_node

    def get_media_data(self, user):
        posts = [post for post in self.query_media_gen(user_id=user['id'])]
        return posts


def scrape_instagram_media(username):
    scraper = Scraper(login_user='tmp_magista', login_pass='magista1400')
    scraper.authenticate_with_login()
    page_info_url = USER_URL.format(username)

    data = scraper.get_data(page_info_url)

    try:
        user_info = json.loads(data)['graphql']['user']
    except:
        logger('cant get user info')
        raise CustomException(500, 'cant get user info')

    if user_info['is_private']:
        print('Private Page')
        raise CustomException(400, "Your page is private")

    profile_info = {
        'username': username,
        'id': user_info['id'],
        'is_private': user_info['is_private'],
        'posts_count': user_info['edge_owner_to_timeline_media']['count'],
        'profile_pic_url': user_info['profile_pic_url'],
        'is_business_account': user_info['is_business_account'],
        'is_professional_account': user_info['is_professional_account'],
        'category_enum': user_info['category_enum'],
        'category_name': user_info['category_name'],
    }

    return scraper.get_media_data(profile_info)


def write_user_media_query_data(username, user_posts_data):
    file_name = f'{username}_media_query.json'
    file_dir = os.path.join(settings.MEDIA_ROOT, 'shop', username)
    file_name_path = os.path.join(file_dir, file_name)
    os.makedirs(file_dir, exist_ok=True)

    json_media_data = json.dumps(user_posts_data, indent=4, ensure_ascii=False)

    file = open(file_name_path, 'w', encoding='utf-8')
    file.write(json_media_data)
    file.close()


def save_preview_images(username):
    try:
        post_preview_data = read_user_media_query_data(username)
    except:
        raise CustomException(500, "Can't get page preview data")

    for post_data in post_preview_data:
        file_dir = os.path.join(settings.MEDIA_ROOT, 'shop', username, post_data['id'])
        os.makedirs(file_dir, exist_ok=True)
        download_and_save_media(post_data['thumbnail_src'], file_dir, 'display_image.jpg')


def read_user_media_query_data(username):
    file_name = f'{username}_media_query.json'
    file_dir = os.path.join(settings.MEDIA_ROOT, 'shop', username)
    file_name_path = os.path.join(file_dir, file_name)

    file = open(file_name_path, 'r', encoding='utf-8')
    file_data = file.read()
    file.close()

    file_data = json.loads(file_data)
    return file_data


def get_page_preview_data(username):
    file_data = read_user_media_query_data(username)
    return_data = []
    print(settings.MEDIA_URL)

    index = 0
    for post_data in file_data:
        display_img_full_path = f"media/shop/{username}/{post_data['id']}/display_image.jpg"

        tmp_dict = {
            "index": index,
            "id": post_data['id'],
            "thumbnail_src": "http://127.0.0.1:8000/" + display_img_full_path
        }

        return_data.append(tmp_dict)
        index += 1

    return return_data


def download_and_save_media(download_url, save_path, file_name):
    response = requests.get(download_url)
    save_full_path = os.path.join(save_path, file_name)
    open(save_full_path, 'wb').write(response.content)
