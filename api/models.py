from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


# Create your models here.
class User(AbstractUser):
    pass

class Monitor(models.Model):
    name = models.CharField(max_length=100)
    url = models.URLField(max_length=200)
    check_interval = models.PositiveIntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(1440)])
    is_active = models.BooleanField(default=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="monitors")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "url"],
                name="unique_url_per_owner"
            )
        ]

    def __str__(self):
        return f"{self.name}: {self.url}"

class CheckResult(models.Model):
    monitor = models.ForeignKey(Monitor, on_delete=models.CASCADE, related_name="results")
    status_code = models.PositiveSmallIntegerField(null=True, blank=True)
    response_time_ms = models.FloatField(null=True, blank=True)
    is_up = models.BooleanField()
    error_message = models.CharField(max_length=255, blank=True)
    checked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['monitor', '-checked_at'])
        ]
        ordering = ['-checked_at']

    def __str__(self):
        return f"{self.monitor.name}: {'UP' if self.is_up else 'DOWN'}, checked at {self.checked_at}"

class Alert(models.Model):
    monitor = models.ForeignKey(Monitor, on_delete=models.CASCADE, related_name="alerts")
    message = models.CharField(max_length=255)
    resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.message}"