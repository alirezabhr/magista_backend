from django.db import models


class Scraper(models.Model):
    username = models.CharField(max_length=30)
    password = models.CharField(max_length=30)
    user_id = models.BigIntegerField()
    nonce = models.CharField(max_length=120, blank=True)
    is_active = models.BooleanField(default=True)
    is_working = models.BooleanField(default=False)
    scrape_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.username} - {self.scrape_count}"
