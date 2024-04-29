# Generated by Django 3.2 on 2024-04-29 13:06

import django.core.validators
from django.db import migrations, models

import products.fields


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="url",
            field=models.URLField(default=""),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="product",
            name="discount",
            field=products.fields.RegexpIntegerField(
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(100),
                ]
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="price",
            field=products.fields.RegexpIntegerField(),
        ),
    ]
