from django_rq.decorators import job
from django.apps import apps
from django.conf import settings
from morningcreative.mail.tasks import send_email


@job('default', timeout='1m')
def email_sponsorship(pk):
    from .models import Sponsorship

    obj = Sponsorship.objects.filter(pk=pk).first()
    if obj is None:
        return

    send_email(
        'New sponsorship',
        'monetisation/sponsorship_email.md',
        {
            'object': obj
        },
        (settings.DEFAULT_FROM_NAME, settings.DEFAULT_FROM_EMAIL)
    )


@job('default', timeout='1m')
def email_sponsorship_results(
    pk,
    delivery_count,
    open_count,
    click_count,
    link_content_type,
    link_pk
):
    from .helpers import get_current_price
    from .models import Sponsorship

    sponsorship = Sponsorship.objects.filter(pk=pk).first()
    if sponsorship is None:
        return

    open_rate = 0
    if delivery_count:
        open_rate = open_count / delivery_count * 100

    LinkModel = apps.get_model(*link_content_type)
    link_obj = LinkModel.objects.get(pk=link_pk)

    send_email(
        'Your sponsorship of the Morning Creative Journal Prompt',
        'monetisation/sponsorship_results_email.md',
        {
            'object': sponsorship,
            'delivery_count': delivery_count,
            'open_rate': open_rate,
            'click_count': click_count,
            'issue': link_obj
        },
        (
            sponsorship.sponsor.name,
            sponsorship.sponsor.email
        )
    )
