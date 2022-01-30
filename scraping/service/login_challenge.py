from .scrape import Scraper

scraper = Scraper()
checkpoint_url = input('checkpoint url')
scraper.login_challenge(checkpoint_url)
