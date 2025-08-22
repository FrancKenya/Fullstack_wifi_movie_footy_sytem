from django.db import models
from django.utils import timezone

class Package(models.Model):
    """
    Package model
    """
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.PositiveIntegerField()
    bandwidth_limit = models.CharField(max_length=50, blank=True)
    max_device = models.PositiveIntegerField(default=1)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)