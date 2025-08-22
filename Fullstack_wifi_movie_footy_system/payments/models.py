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

    class Meta:
        indexes = [models.Index(fields=['active'])]

    def __str__(self):
        return f"{self.name} - KES {self.price} / {self.duration} min"

class SessionStatus(models.TextChoices):
    """
    Session status choices
    """
    PENDING = "PENDING", "Pending"
    PAID = "PAID", "Paid"
    ACTIVE = "ACTIVE", "Active"
    EXPIRED = "EXPIRED", "Expired"
    FAILED = "FAILED", "Failed"

class PaymentStatus(models.TextChoices):
    """
    Payment status choices
    """
    PENDING = "PENDING", "Pending"
    SUCCESS = "SUCCESS", "Success"
    FAILED = "FAILED", "Failed"

class UserSession(models.Model):
    """
    User session model
    """
    package = models.ForeignKey(
        Package, on_delete=models.PROTECT, related_name="sessions")
    msisdn = models.CharField(max_length=15) # Clients phone number
    mac_address = models.CharField(max_length=17, blank=True, null=True)
    status = models.CharField(
        max_length=10, choices=SessionStatus.choices, default=SessionStatus.PENDING)
    checkout_request_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    mpesa_receipt = models.CharField(max_length=30, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    start_time = models.DateTimeField(blank=True, null=True)
    expiry_time = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        """
        Meta class
        """
        indexes = [
            models.Index(fields=['msisdn']),
            models.Index(fields=['status']),
        ]


class Payment(models.Model):
    """
    Payment model
    """
    session = models.ForeignKey(UserSession, on_delete=models.CASCADE, related_name="payments")
    msisdn = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    checkout_request_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    mpesa_receipt = models.CharField(max_length=30, blank=True, null=True)
    raw_payload = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
