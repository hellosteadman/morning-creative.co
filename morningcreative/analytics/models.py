from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone
from hashlib import sha256
from urllib.parse import urlencode, urlsplit, parse_qs, urlunsplit
from uuid import uuid4


class TrackedLink(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='tracked_links'
    )

    object_id = models.JSONField()
    content_object = GenericForeignKey('content_type', 'object_id')
    url = models.URLField('URL', max_length=512, db_index=True)
    text = models.TextField(null=True, blank=True)
    ordering = models.PositiveIntegerField(default=0)
    campaign = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.url

    @transaction.atomic
    def click(self, request):
        user_agent = request.META['HTTP_USER_AGENT']
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        user_id = request.GET.get('u') or None
        medium = request.GET.get('m') or None

        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        data = '\n'.join((user_agent, ip)).encode('utf-8')
        hashed = sha256(data).hexdigest()
        now = timezone.now()

        if self.clicks.select_for_update().filter(
            user_id=user_id,
            profile_hash=hashed
        ).update(
            clicks=models.F('clicks') + 1,
            last_clicked=now,
            medium=medium
        ):
            return self.clicks.filter(
                user_id=user_id,
                profile_hash=hashed
            ).latest()

        return self.clicks.create(
            user_id=user_id,
            profile_hash=hashed,
            medium=medium,
            clicks=1,
            last_clicked=now
        )

    def get_tracking_url(self, user_id=None, medium=None):
        query = {}

        if user_id:
            query['u'] = user_id

        if medium:
            query['m'] = medium

        return 'http%s://%s%s%s' % (
            not settings.DEBUG and 's' or '',
            settings.DOMAIN,
            reverse('tracked_link_redirect', args=(self.pk,)),
            any(query) and ('?' + urlencode(query)) or ''
        )

    class Meta:
        unique_together = (
            'content_type',
            'object_id',
            'text',
            'url',
            'campaign'
        )

        ordering = ('ordering', 'url')


class TrackedLinkClick(models.Model):
    link = models.ForeignKey(
        TrackedLink,
        on_delete=models.CASCADE,
        related_name='clicks'
    )

    user_id = models.JSONField(null=True)
    profile_hash = models.CharField(max_length=64, editable=False)
    clicks = models.PositiveIntegerField(default=0, editable=False)
    last_clicked = models.DateTimeField(editable=False)
    medium = models.CharField(max_length=30, null=True, editable=False)

    def get_destination_url(self):
        scheme, location, path, query, fragment = urlsplit(self.link.url)
        query = parse_qs(query)

        if 'utm_source' not in query:
            query['utm_source'] = 'morningcreative'

        if self.medium and 'utm_medium' not in query:
            query['utm_medium'] = self.medium

        if self.link.campaign and 'utm_campaign' not in query:
            query['utm_campaign'] = self.link.campaign

        query = urlencode(query, doseq=True)
        return urlunsplit((scheme, location, path, query, fragment))

    def __str__(self):
        return self.get_destination_url()

    class Meta:
        db_table = 'analytics_trackedlink_click'
        unique_together = ('user_id', 'profile_hash', 'link')
        ordering = ('-last_clicked',)
        get_latest_by = 'last_clicked'
