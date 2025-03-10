# Generated by Django 3.2.7 on 2021-12-20 06:01

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Scraper',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=30)),
                ('password', models.CharField(max_length=30)),
                ('is_working', models.BooleanField(default=False)),
                ('scrape_count', models.IntegerField(default=0)),
            ],
        ),
    ]
