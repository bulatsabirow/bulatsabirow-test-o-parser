from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=1024)
    description = models.TextField()
    price = models.FloatField()
    discount = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    image_url = models.URLField()

    def __str__(self):
        return self.name
