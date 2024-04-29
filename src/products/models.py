from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from products.fields import RegexpIntegerField


class Product(models.Model):
    name = models.CharField(max_length=1024)
    description = models.TextField()
    price = RegexpIntegerField(group="price", regexp=r"(?P<price>.+)(?=\u2009₽)")
    discount = RegexpIntegerField(
        group="discount",
        regexp=r"(?<=−)(?P<discount>\d+)(?=%)",
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    url = models.URLField(max_length=1024)
    image_url = models.URLField(max_length=1024)

    def __str__(self):
        return self.name
