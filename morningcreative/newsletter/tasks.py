from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.urls import reverse
from django.utils import timezone
from django_rq.decorators import job
from morningcreative.analytics.models import TrackedLink
from morningcreative.mail.tasks import send_email
import re
import requests


MARKDOWN_LINK_REGEX = r'\[([^\]]+)\]\(([^\)]+)\)'
IPINFO_API_URL = settings.IPINFO_API_URL
IPINFO_API_KEY = settings.IPINFO_API_KEY


@transaction.atomic
@job('default', timeout='1m')
def set_subscriber_location(pk, ip):
    from .models import Subscriber

    if ip == '127.0.0.1' and settings.DEBUG:
        response = requests.get(
            IPINFO_API_URL % '',
            headers={
                'Authorization': 'Bearer %s' % IPINFO_API_KEY
            }
        )

        response.raise_for_status()
        response = response.json()
        ip = response['ip']

    response = requests.get(
        IPINFO_API_URL % ip,
        headers={
            'Authorization': 'Bearer %s' % IPINFO_API_KEY
        }
    )

    response.raise_for_status()
    response = response.json()

    for obj in Subscriber.objects.filter(pk=pk).select_for_update():
        obj.city = response.get('city')
        obj.country = response.get('country')
        obj.save()


@job('default', timeout='1m')
def welcome_subscriber(pk):
    from .models import Subscriber, Post

    subscriber = Subscriber.objects.filter(pk=pk).first()
    if subscriber is None:
        return

    latest_post = Post.objects.filter(
        published__lte=timezone.now()
    ).order_by(
        '-published'
    ).first()

    send_email(
        subject='Welcome to the Morning Creative Journal Prompt',
        body_template='newsletter/welcome_email.md',
        html_template='newsletter/welcome_email.html',
        body_context={
            'latest_post': latest_post
        },
        recipient=subscriber.get_formatted_address(),
        unsubscribe_url=reverse('unsubscribe')
    )

    send_email(
        subject='New subscriber to the Morning Creative Journal Prompt',
        body_template='newsletter/new_subscriber_email.md',
        body_context={
            'object': subscriber,
            'latest_post': latest_post and latest_post.published
        },
        recipient=('Mark Steadman', 'mark@hellosteadman.com')
    )


@job('default', timeout='1m')
def send_test_delivery(pk, email):
    from .models import Post

    obj = Post.objects.filter(pk=pk).first()
    if obj is None:
        return

    if obj.sponsorship_id:
        sponsor = obj.sponsorship.message
    else:
        sponsor = ''

    send_email(
        subject=obj.title,
        body_template='newsletter/email_body.md',
        html_template='newsletter/email_body.html',
        body_context={
            'object': obj,
            'sponsor': sponsor,
            'episode': obj.episode,
            'prompt': obj.prompt,
            'body': obj.body
        },
        recipient=email,
        unsubscribe_url=reverse('unsubscribe')
    )


@transaction.atomic
@job('default', timeout='5m')
def send_deliveries(pk):
    from .models import Post

    obj = Post.objects.filter(pk=pk).first()
    if obj is None:
        return

    for recipient in obj.get_recipients().iterator():
        delivery = obj.deliveries.select_for_update().filter(
            recipient=recipient
        ).first()

        if delivery is None:
            delivery = obj.deliveries.create(
                recipient=recipient
            )

        if delivery.delivered is None:
            transaction.on_commit(delivery.deliver)


@transaction.atomic
@job('default', timeout='1m')
def send_delivery(pk):
    from .models import Delivery

    obj = Delivery.objects.select_for_update().filter(pk=pk).first()
    if obj is None:
        return

    content_type = ContentType.objects.get_for_model(obj.post)
    ctx = {
        'link_ordering': 0
    }

    def replacer(match):
        inner, href = match.groups()
        if href.startswith('mailto:'):
            return '<%s>' % href

        start, end = match.span()
        tracked_link, created = TrackedLink.objects.get_or_create(
            content_type=content_type,
            object_id=obj.post_id,
            url=href,
            text=inner,
            campaign=(
                obj.post.published or timezone.now()
            ).strftime('%Y-%m-%d'),
            defaults={
                'ordering': ctx['link_ordering']
            }
        )

        ctx['link_ordering'] += 1
        tracked_url = tracked_link.get_tracking_url(
            user_id=str(obj.pk),
            medium='email'
        )

        return '[%s](%s)' % (inner, tracked_url)

    if obj.post.sponsorship_id:
        sponsor = re.sub(MARKDOWN_LINK_REGEX, replacer, obj.post.sponsorship.message)
    else:
        sponsor = ''

    send_email(
        subject=obj.post.title,
        body_template='newsletter/email_body.md',
        html_template='newsletter/email_body.html',
        body_context={
            'object': obj.post,
            'sponsor': sponsor,
            'body': re.sub(MARKDOWN_LINK_REGEX, replacer, obj.post.body)
        },
        recipient=obj.recipient.get_formatted_address(),
        tracking_pixel_url=reverse(
            'track_delivery_open', args=(obj.pk,)
        ),
        unsubscribe_url=reverse('unsubscribe')
    )

    obj.delivered = timezone.now()
    obj.save()
