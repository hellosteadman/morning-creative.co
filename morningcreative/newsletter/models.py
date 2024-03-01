from django.conf import settings
from django.contrib.auth.models import User
from django.db import models, transaction
from django.utils import timezone
from email.utils import formataddr
from markdownx.models import MarkdownxField
from morningcreative.analytics.helpers import get_user_agent_info
from morningcreative.monetisation.models import Sponsorship
from uuid import uuid4
from .query import SubscriberQuerySet
from .tasks import (
    set_subscriber_location,
    send_deliveries,
    send_test_delivery,
    send_delivery
)


class Post(models.Model):
    title = models.CharField(max_length=100)
    published = models.DateField(null=True, blank=True)

    sponsorship = models.ForeignKey(
        Sponsorship,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    episode = models.ForeignKey(
        'podcast.Episode',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    prompt = models.ForeignKey(
        'prompts.Prompt',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    body = MarkdownxField(null=True, blank=True)
    cued_for_delivery = models.BooleanField(default=False, editable=False)

    def __str__(self):
        return self.title

    def send_test_delivery(self, email):
        send_test_delivery.delay(self.pk, email)

    def get_recipients(self):
        return Subscriber.objects.exclude(
            email__in=Unsubscriber.objects.values_list('email', flat=True)
        )

    @transaction.atomic
    def deliver(self, delayed=True):
        self.cued_for_delivery = True
        self.save(
            update_fields=('cued_for_delivery',)
        )

        if delayed:
            transaction.on_commit(
                lambda: send_deliveries.delay(self.pk)
            )
        else:
            transaction.on_commit(
                lambda: send_deliveries(self.pk)
            )

        transaction.on_commit(self.publish)

    @property
    def successful_deliveries(self):
        return self.deliveries.filter(
            delivered__isnull=False
        )

    def save(self, *args, **kwargs):
        if self.published and self.sponsorship is None:
            if self.pk is None or not self.deliveries.count():
                q = models.Q(
                    end=None
                ) | models.Q(
                    start=self.published
                )

                fallback = None

                for sponsorship in Sponsorship.objects.filter(q).order_by(
                    'start',
                    '-stripe_id'
                ).distinct():
                    if sponsorship.start is None or sponsorship.end is None:
                        fallback = sponsorship
                        continue

                    date = sponsorship.start

                    while date <= self.published:
                        if date == self.published:
                            self.sponsorship = sponsorship
                            break

                        date += timezone.timedelta(days=7)

                    if self.sponsorship is not None:
                        break

                if self.sponsorship is None and fallback is not None:
                    self.sponsorship = fallback

        super().save(*args, **kwargs)

    class Meta:
        ordering = ('-published',)
        get_latest_by = 'published'


class Subscriber(models.Model):
    objects = SubscriberQuerySet.as_manager()

    uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=255)
    subscribed = models.DateTimeField(auto_now_add=True)
    city = models.CharField(max_length=100, null=True, editable=False)
    country = models.CharField(
        max_length=2,
        null=True,
        editable=False,
        choices=settings.COUNTRIES.items()
    )

    last_seen = models.DateTimeField(null=True, editable=False)

    def __str__(self):
        return self.name

    def get_formatted_address(self):
        return formataddr(
            (
                self.name,
                self.email
            )
        )

    @transaction.atomic
    def set_active(self, request, force=False):
        now = timezone.now()
        update = False

        if force or self.last_seen is None:
            update = True
        else:
            delta = (now - self.last_seen).total_seconds()
            if delta >= 3600:
                update = True

        if update:
            self.last_seen = now
            self.save()

            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')

            if ip and not settings.DEBUG:
                transaction.on_commit(
                    lambda: set_subscriber_location.delay(
                        self.pk,
                        ip
                    )
                )

    class Meta:
        ordering = ('-subscribed',)
        get_latest_by = 'subscribed'


class Unsubscriber(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    email = models.EmailField(max_length=255)
    unsubscribed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

    class Meta:
        ordering = ('-unsubscribed',)
        get_latest_by = 'unsubscribed'


class Delivery(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='deliveries'
    )

    recipient = models.ForeignKey(
        Subscriber,
        on_delete=models.CASCADE,
        related_name='deliveries'
    )

    delivered = models.DateTimeField(null=True, editable=False)

    def deliver(self):
        send_delivery.delay(self.pk)

    @transaction.atomic
    def open(self, request):
        user_agent = request.META['HTTP_USER_AGENT']
        request.set_subscriber(self.recipient)
        score = 0
        occurred = timezone.now()
        seconds_between = (occurred - self.delivered).total_seconds()

        if seconds_between < 60:
            score -= 2

        if (agent := get_user_agent_info(user_agent)) is not None:
            if agent['bot']:
                score -= 2
            else:
                score += 1
        else:
            score -= 1

        if not self.opens.filter(
            occurred__gte=occurred - timezone.timedelta(minutes=5),
            app=agent and agent['browser'] or '',
            platform=agent and agent['platform'] or '',
            device=agent and agent['device_type'] or ''
        ).select_for_update().exists():
            self.opens.create(
                app=agent and agent['browser'] or '',
                platform=agent and agent['platform'] or '',
                device=agent and agent['device_type'] or '',
                occurred=occurred,
                score=score
            )

    class Meta:
        verbose_name_plural = 'deliveries'


class Open(models.Model):
    delivery = models.ForeignKey(
        Delivery,
        related_name='opens',
        on_delete=models.CASCADE
    )

    score = models.IntegerField(default=0)
    app = models.CharField(max_length=100, null=True, blank=True)
    platform = models.CharField(max_length=100, null=True, blank=True)
    device = models.CharField(max_length=100, null=True, blank=True)
    occurred = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.app

    class Meta:
        ordering = ('-occurred',)
        get_latest_by = 'occurred'
