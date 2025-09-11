from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserSession
from .models import Transaction

@receiver(post_save, sender=Transaction)
def update_sessions_on_status_change(sender, instance, **kwargs):
    """Update sessions when transaction status changes"""
    if instance.status in ['FAILED', 'EXPIRED']:
        UserSession.objects.filter(transaction=instance, is_active=True).update(is_active=False)

from django.utils import timezone
from django.core.management.base import BaseCommand
class Command(BaseCommand):
    help = "Expire transactions that are past expiry_time"

    def handle(self, *args, **kwargs):
        now = timezone.now()
        expired = Transaction.objects.filter(
            status='SUCCESSFUL', expiry_time__lt=now
        )
        count = expired.update(status='EXPIRED')
        self.stdout.write(f"Marked {count} transactions as expired")
