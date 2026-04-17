from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('staff', 'Staff'),
        ('Depot Manager', 'Depot Manager'),
    ]
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='staff')

    def __str__(self):
        return self.username