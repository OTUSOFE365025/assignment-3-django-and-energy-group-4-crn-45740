from django.db import models

class Product(models.Model):
    upc = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=9, decimal_places=2)

    def __str__(self):
        return f"{self.upc} - {self.name} (${self.price})"
