from django.conf import settings
from django.utils import timezone
from .models import Sponsorship


def get_current_price():
    current_price = 0
    last_sponsorship = Sponsorship.objects.exclude(
        stripe_id=None
    ).order_by('-price').first()

    if last_sponsorship is not None:
        current_price = last_sponsorship.price

    current_price += settings.ISSUE_SPONROSHIP_INCREMENT
    return int(current_price)


def slots_available(threshold=None):
    if isinstance(threshold, timezone.timedelta):
        threshold = timezone.now() + threshold
    elif threshold is None:
        threshold = timezone.now() + timezone.timedelta(days=90)

    return not Sponsorship.objects.filter(
        end__gte=threshold
    ).exists()
