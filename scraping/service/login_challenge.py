from scrape import Scraper

username = input('username: ')
password = input('password: ')

scraper = Scraper(username, password)

try:
    scraper.authenticate_with_login()
except Exception as e:
    print(e)

checkpoint_url = input('checkpoint url: ')
scraper.login_challenge(checkpoint_url)
