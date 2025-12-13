from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
import random
from datetime import datetime, timedelta
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    username = None  # remove username field
    f_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="First Name")
    l_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Last Name")
    email = models.EmailField(max_length=200, unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        name = f"{self.f_name or ''} {self.l_name or ''}".strip()
        return name if name else self.email


class EmailOTP(models.Model):
    PURPOSE_CHOICES = [
        ('register', 'Registration'),
        ('login', 'Login'),
    ]
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    purpose = models.CharField(max_length=10, choices=PURPOSE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"{self.user.email} - {self.otp} ({self.purpose})"