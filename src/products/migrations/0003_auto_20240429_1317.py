# Generated by Django 3.2 on 2024-04-29 13:17

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0002_auto_20240429_1306"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="image_url",
            field=models.URLField(max_length=1024),
        ),
        migrations.AlterField(
            model_name="product",
            name="url",
            field=models.URLField(max_length=1024),
        ),
    ]