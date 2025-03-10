# Generated by Django 3.2.7 on 2022-03-28 10:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('shop', '0021_auto_20220213_1922'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shop',
            name='email',
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.CreateModel(
            name='ShopCreationStep',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('instagram_username', models.CharField(max_length=30, unique=True)),
                ('phone', models.CharField(max_length=11, unique=True)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('step', models.CharField(choices=[('REQUESTED', 'Requested'), ('SUBMITTED', 'Submitted'), ('CREATED', 'Created')], default='REQUESTED', max_length=10)),
                ('vendor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applicant', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
