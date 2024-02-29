from django.conf import settings
from django.template import Library
from ..helpers import get_current_price, slots_available
from ..models import Announcement


register = Library()


@register.inclusion_tag('monetisation/sponsorship_cta.md')
def sponsorship_cta():
    return {
        'available': slots_available(),
        'pricing': {
            'current': get_current_price(),
            'increment': settings.ISSUE_SPONROSHIP_INCREMENT
        },
        'announcement': Announcement.objects.order_by('-date').first()
    }
