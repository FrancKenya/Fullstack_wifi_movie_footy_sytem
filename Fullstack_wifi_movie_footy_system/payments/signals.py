from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserSession
from .models import Transaction

@receiver(post_save, sender=Transaction)
def update_sessions_on_status_change(sender, instance, **kwargs):
    """Update sessions when transaction status changes"""
    if instance.status in ['FAILED', 'EXPIRED']:
        UserSession.objects.filter(transaction=instance, is_active=True).update(is_active=False)
