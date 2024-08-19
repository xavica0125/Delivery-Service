from django.db import models
from django.contrib.auth.models import User
# Create your models here.

"""User Preferences model that stores the user's preferences. Relationship with User model is defined as OneToOneField using user_id as the primary key/foreign key."""
class Preferences(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    business = models.BooleanField(default=False, null=True)
    entertainment = models.BooleanField(default=False, null = True)
    general = models.BooleanField(default=False, null = True)
    health = models.BooleanField(default=False, null = True)
    science = models.BooleanField(default=False, null = True)    
    sports = models.BooleanField(default=False, null = True)
    technology = models.BooleanField(default=False, null = True)

    def __str__(self):
        return str(self.user_id)