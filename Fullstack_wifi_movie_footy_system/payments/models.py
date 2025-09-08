from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from datetime import timedelta

class Package(models.Model):
    """
    Package model
    """
    name = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    duration_value = models.PositiveIntegerField() # package duration value e.g 30
    duration_unit = models.CharField(max_length=10,
                                     choices=[(
                                         "MINUTES", "Minutes"),
                                         ("HOURS", "Hours"), ("DAYS", "Days"),
                                         ("MONTHS", "Months")])  # Package duration unit e.g MINUTES, Hours
    max_devices = models.PositiveSmallIntegerField(default=1,
                                                   validators=[MinValueValidator(1)])
    active = models.BooleanField(default=True)  # Available to purchase
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_expiry(self, start_time):
        """
        Calculates the expiry time for the package duration based on the start time
        Months treated as 30 days fixed period not calendar relatd since time of transaction
        """
        # Mapping the duration unit to a timedelta argument and multiplier
        unit_map = {
            "MINUTES": ("minutes", 1),
            "HOURS": ("hours", 1),
            "DAYS": ("days", 1),
            "MONTHS": ("months", 30),
        }
        # Handle invalid duration units by raising a value error
        if self.duration_unit not in unit_map:
            raise ValueError(f"Invalid duration unit: {self.duration_unit}")

        unit, multiplier = unit_map[self.duration_unit]
        duration_in_units = self.duration_value * multiplier

        # create the timedelta
        delta_args = {unit: duration_in_units}  # Create a dictionary of the timedelta arguments
        return start_time + timedelta(**delta_args)  # return the expiry time


    class Meta:
        indexes = [models.Index(fields=['active'])]  # Display active packages on captive portal

    def __str__(self):
        """
        Package string representation
        """
        return f"{self.name} - KES {self.price} / {self.duration_value} {self.duration_unit.lower()}"

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


class Transaction(models.Model):
    """
    Transaction model
    """
    package = models.ForeignKey(
        Package, on_delete=models.PROTECT, related_name="transactions")  # Link to the package model
    # Client Identification using device MAC address
    mac_address = models.CharField(max_length=17)
    mpesa_receipt = models.CharField(max_length=30, blank=True, null=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    # When payment was initiated
    initiated_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(blank=True, null=True) # Time of payment confirmation

    expiry_time = models.DateTimeField(null=True, blank=True) # Time of package expiry calculated after payment confirmation
    is_successful = models.BooleanField(default=False) # Payment status

    def save(self, *args, **kwargs):
        """Calculate and save expire only after payment is confirmed method"""
        if self.is_successful and not self.expiry_time:  # Only calculate expiry if payment is successful
            start_time = self.paid_at or timezone.now()
            self.expiry_time = self.package.calculate_expiry(start_time)
        super().save(*args, **kwargs)

    def __str__(self):
        """
        Transaction string representation
        """
        return f"{self.mac_address} - {self.package.name} ({'Success' if self.is_successful else 'Pending'})"