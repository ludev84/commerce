from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    watchlist = models.ManyToManyField("Listing", blank=True, related_name="watchers")

    def __str__(self):
        return self.username


class Listing(models.Model):
    class Category(models.TextChoices):
        ELECTRONICS = "electronics", "Electronics"
        FASHION = "fashion", "Fashion"
        HOME = "home", "Home"
        TOYS = "toys", "Toys"

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=64)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    category = models.CharField(
        max_length=64,
        choices=Category,
    )
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    offer = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.user.username} offers {self.offer} dollars for {self.listing}."


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    content = models.CharField(max_length=250)

    def __str__(self):
        return f"Comment by {self.user.username}"
