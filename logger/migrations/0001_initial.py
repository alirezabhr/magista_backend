# Generated by Django 3.2.7 on 2021-12-14 11:36

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location', models.CharField(max_length=50)),
                ('key', models.CharField(max_length=25, null=True)),
                ('value', models.CharField(max_length=100, null=True)),
                ('message', models.TextField(null=True)),
                ('critical', models.BooleanField()),
                ('is_customer_project', models.BooleanField()),
                ('time', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
