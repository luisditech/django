from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime
from .managers import CustomUserManager

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class User(AbstractUser):
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    email = models.EmailField(unique=True)
    recovery_code= models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    class Meta:
        app_label = 'core'
    def is_recovery_code_expired(self):
        if self.recovery_code_expiration:
            return datetime.now() > self.recovery_code_expiration
        return False
    def __str__(self):
        return self.username