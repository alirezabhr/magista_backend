import json

from scraping.service.scrape import Scraper


def run_script():
    username = input('username: ')
    password = input('password: ')

    scraper = Scraper(username, password)

    try:
        scraper.try_to_authenticate()
    except Exception as e:
        print(e)
        checkpoint_url = input('checkpoint url: ')
        cookies = scraper.login_challenge(checkpoint_url)

        authenticated = scraper.test_authentication()
        print('authenticated' if authenticated else 'not authenticated')

        print('Cookies: ')
        if cookies:
            print(json.dumps(cookies.get_dict()))
            print(json.dumps(scraper.session.cookies.get_dict()))
            scraper.save_cookies()


run_script()
