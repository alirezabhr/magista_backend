# Generated by Django 3.2.7 on 2022-02-06 05:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scraping', '0005_alter_scraper_nonce'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='scraper',
            name='cookie_json',
        ),
    ]
