import json

from scraping.service.constants import USER_URL
from scraping.service.scrape import Scraper, write_user_profile_info_data, read_user_media_query_data, \
    save_preview_images, get_page_preview_data, save_profile_image


def get_data(username):
    scraper_username = input('scraper username: ')
    scraper_password = input('scraper password: ')

    scraper = Scraper(scraper_username, scraper_password)

    try:
        scraper.try_to_authenticate()
    except Exception as e:
        print(e)
        checkpoint_url = input('checkpoint url: ')
        cookies = scraper.login_challenge(checkpoint_url)
        print('Cookies: ')
        if cookies:
            print(json.dumps(cookies.get_dict()))

    page_info_url = USER_URL.format(username)
    data = scraper.get_data(page_info_url)

    try:
        user_info = json.loads(data)['graphql']['user']
    except Exception as exception:
        print('cant get user info')
        print(exception)
        raise Exception(503, 'cant get user info')

    if user_info['is_private']:
        print('Private Page')
        raise Exception(451, "پیج مورد نظر پرایوت است")

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

    write_user_profile_info_data(username, profile_info)

    media_data = scraper.get_media_data(profile_info['id'], '')

    return media_data


def get_user_data():
    instagram_username = input('instagram username: ')

    """
    try:
        data = get_data(instagram_username)
        write_user_media_query_data(instagram_username, data)
        # THIS FUNCTION IS NOT IMPORTED
    except Exception as exc:
        print(f' exception: {exc}')
        return
    """

    has_next = True
    page = 1
    posts_preview_data = read_user_media_query_data(instagram_username)
    print('data had been read')
    while has_next:
        # if page < 19:
        #     page += 1
        #     continue
        print(f'downloading post images. page: {page}')
        save_preview_images(instagram_username, page, posts_preview_data)
        response_data = get_page_preview_data(instagram_username, page, posts_preview_data)
        has_next = response_data['has_next']
        page += 1

    print('post images Downloaded')
    try:
        save_profile_image(instagram_username)
    except Exception as exc:
        print('exception again')
        print(exc)
        return

    print('Done')


get_user_data()
