import requests
import json
import hashlib
import sys

from constants import *


def logger(message):
    print('----------\n')
    print(message)
    print('\n----------')


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
            raise Exception('problem in authenticate_with_login')

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
        else:
            print(response.status_code)

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
