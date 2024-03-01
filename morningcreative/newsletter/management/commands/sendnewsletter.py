from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from morningcreative.newsletter.models import Delivery
from morningcreative.newsletter.tasks import send_delivery


class Command(BaseCommand):
    help = 'Send scheduled newsletter emails'

    def handle(self, *args, **options):
        for obj in Delivery.objects.filter(
            scheduled__lte=timezone.now(),
            delivered=None
        ).iterator():
            with transaction.atomic():
                send_delivery(obj.pk)
