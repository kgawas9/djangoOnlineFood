from django.db import models

from accounts.models import User
from menu.models import FoodItem
# Create your models here.

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    food_item = models.ForeignKey(FoodItem, on_delete = models.CASCADE)
    quantity = models.PositiveBigIntegerField()
    created_at = models.DateTimeField(auto_now_add = True)
    modified_at = models.DateTimeField(auto_now = True)

    def __str__(self):
        return self.user.username
