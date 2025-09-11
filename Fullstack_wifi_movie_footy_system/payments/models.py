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



class Transaction(models.Model):
    """
    Transaction model
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SUCCESSFUL', 'Successful'),
        ('FAILED', 'Failed'),
        ('EXPIRED', 'Expired')

    ]
    package = models.ForeignKey(
        Package, on_delete=models.PROTECT, related_name="transactions")  # Link to the package model
    # Client Identification using device MAC address
    mac_address = models.CharField(max_length=17)
    mpesa_receipt = models.CharField(max_length=30, unique=True, blank=True, null=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    # When payment was initiated
    initiated_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(blank=True, null=True) # Time of payment confirmation

    expiry_time = models.DateTimeField(null=True, blank=True) # Time of package expiry calculated after payment confirmation
    payer_phone = models.CharField(max_length=15, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    failure_reason = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        """Calculate and save expire only after payment is confirmed method"""
        if self.status == 'SUCCESSFUL' and not self.expiry_time:  # Only calculate expiry if payment is successful
            start_time = self.paid_at or timezone.now()
            self.expiry_time = self.package.calculate_expiry(start_time)
        # if expired mark as expired
        if self.status == 'SUCCESSFUL' and self.expiry_time and self.expiry_time < timezone.now():
            self.status = 'EXPIRED'
        super().save(*args, **kwargs)


    class Meta:
        """
        Transaction metadata
        """
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['mpesa_receipt']),
        ]


    def __str__(self):
        """
        Transaction string representation
        """
        return f"{self.mac_address} - {self.package.name} ({self.status})"

class UserSession(models.Model):
    """"
    Represents an active client session on the network tied to a specific transaction
    """
    id = models.AutoField(primary_key=True)
    transaction = models.ForeignKey(
        Transaction, on_delete= models.CASCADE, related_name="usersessions")
    mac_address = models.CharField(max_length=17)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)


    def save(self, *args, **kwargs):
        """ Check if transaction is expired before saving session """
        if self.transaction.status == 'SUCCESSFUL' and self.transaction.expiry_time < timezone.now(): #
            # mark that transaction as expired
            self.transaction.status = 'EXPIRED'
            self.transaction.save(update_fields=['status'])

            # End that session ASAP
            self.is_active = False
            self.updated_at = timezone.now()
        else:
            # Ensure only 1 active session per transaction
            UserSession.objects.filter(
                transaction=self.transaction, is_active=True).exclude(id=self.id).update(is_active=False)
        super().save(*args, **kwargs)

    def is_session_valid(self):
        """Validate if session is still usable"""
        if not self.is_active:
            return False
        if self.transaction.expiry_time < timezone.now():
            # Expire session + transaction
            self.is_active = False
            self.updated_at = timezone.now()
            self.transaction.status = 'EXPIRED'
            self.transaction.save(update_fields=['status'])
            self.save(update_fields=['is_active', 'updated_at'])
            return False
        return True

    class Meta:
        """
        UserSession metadata
        """
        indexes = [
            models.Index(fields=['transaction', 'is_active']),
            models.Index(fields=['mac_address', 'is_active']),
        ]


    def __str__(self):
        """
        UserSession string representation
        """
        return f"Session for {self.transaction.mpesa_receipt} ({self.mac_address})"

