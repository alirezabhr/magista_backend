# Generated by Django 3.2.7 on 2021-11-02 11:05

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Discount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('percent', models.PositiveSmallIntegerField()),
                ('description', models.CharField(blank=True, max_length=300)),
                ('is_active', models.BooleanField(default=True)),
                ('start_at', models.DateTimeField()),
                ('end_at', models.DateTimeField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('disabled_at', models.DateTimeField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.SmallIntegerField()),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveSmallIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shortcode', models.CharField(max_length=15)),
                ('display_image', models.CharField(max_length=120, null=True)),
                ('title', models.CharField(blank=True, max_length=100)),
                ('description', models.TextField()),
                ('instagram_link', models.CharField(blank=True, max_length=70)),
                ('rate', models.PositiveSmallIntegerField(null=True)),
                ('is_existing', models.BooleanField(default=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProductAttribute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('value', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='ProductPrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.IntegerField()),
                ('set_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Shop',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('instagram_username', models.CharField(max_length=30, unique=True)),
                ('instagram_id', models.IntegerField(unique=True)),
                ('province', models.CharField(max_length=30)),
                ('city', models.CharField(max_length=30)),
                ('address', models.TextField()),
                ('profile_pic', models.CharField(max_length=80, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
