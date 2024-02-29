from collections import defaultdict
from django.conf import settings
from django.core.cache import cache
from django.core.files.storage import default_storage
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html, strip_tags
from django.utils.safestring import mark_safe
from easy_thumbnails.fields import ThumbnailerImageField
from markdown import markdown
from markdownx.models import MarkdownxField
from taggit.managers import TaggableManager
from tempfile import mkstemp
from .query import EpisodeQuerySet
import logging
import time
import os
import re
import requests


class Episode(models.Model):
    objects = EpisodeQuerySet.as_manager()

    def upload_thumbnail(self, filename):
        return 'podcast/%s/thumbnail%s' % (
            self.number,
            os.path.splitext(filename)[-1]
        )

    def upload_poster(self, filename):
        return 'podcast/%s/poster%s' % (
            self.number,
            os.path.splitext(filename)[-1]
        )

    title = models.CharField(max_length=100, null=True, blank=True)
    number = models.PositiveIntegerField(unique=True)
    published = models.DateField()
    excerpt = models.TextField(null=True, blank=True)

    tags = TaggableManager(
        blank=True,
        related_name='posts'
    )

    thumbnail = ThumbnailerImageField(
        upload_to=upload_thumbnail,
        max_length=255
    )

    poster = ThumbnailerImageField(
        upload_to=upload_poster,
        max_length=255,
        null=True,
        blank=True
    )

    oembed = models.URLField(
        'oEmbed URL',
        max_length=255,
        null=True,
        blank=True
    )

    remote_id = models.CharField(
        'remote ID',
        max_length=255,
        editable=False
    )

    body = MarkdownxField(null=True, blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('episode_detail', args=(self.number,))

    def get_feed_url(self):
        return '/%s/feed/' % self.slug

    def get_comments_url(self):
        return '/%s/comments/' % self.slug

    def get_excerpt(self, first_sentence=False):
        if self.excerpt and not first_sentence:
            return mark_safe(markdown(self.excerpt))

        lines = []

        for line in self.body.splitlines():
            if not line and any(lines):
                break

            if re.match(r'^#+ ', line) is not None:
                break

            if re.match(r'^\d+(?:\.:) ', line) is not None:
                break

            if re.match(r'^\* ', line) is not None:
                break

            if re.match(r'^- ', line) is not None:
                break

            lines.append(line)

        body = ' '.join(lines)
        if first_sentence:
            body = body.split('. ')[0] + '.'
            if '? ' in body:
                body = body.split('? ')[0] + '?'

        return format_html(
            '<p>{}</p>',
            strip_tags(
                markdown(body)
            )
        )

    def get_first_sentence(self):
        return self.get_excerpt(True)

    @property
    def approved_comments(self):
        return self.comments.filter(
            spam=False,
            approved=True
        )

    def get_player_image(self):
        image_filename = 'podcast/%s/player.jpg' % self.number
        match = re.match(
            r'^https?://media\.transistor\.fm/([^/]+)/[^\.]+\.mp3$',
            self.oembed
        )

        if match is None:
            return

        try:
            default_storage.size(image_filename)
        except FileNotFoundError:
            now = timezone.now().replace(
                hour=1,
                minute=0,
                second=0,
                microsecond=0
            )

            player_url = 'https://share.transistor.fm/e/%s' % match.groups()[0]
            response = requests.get(
                'https://screendot.io/api/standard',
                params={
                    'url': player_url + '?_ts=%d' % time.mktime(now.timetuple()),
                    'delay': 5000,
                    'browserWidth': 720,
                    'browserHeight': 180,
                    'width': 1440,
                    'height': 360,
                    'fullPage': 'true'
                },
                headers={
                    'Authorization': 'Bearer %s' % settings.SCREENSHOT_API_KEY
                },
                stream=True
            )

            try:
                response.raise_for_status()
            except Exception:
                logging.error('HTTP exception grabbing player screenshot')
                return

            handle, filename = mkstemp('.jpg')

            try:
                for chunk in response.iter_content(chunk_size=1024*1024):
                    os.write(handle, chunk)
            finally:
                os.close(handle)

            default_storage.save(
                image_filename,
                open(filename, 'rb')
            )

        return default_storage.url(image_filename)

    def get_related_posts(self):
        cachekey = 'episode_%d_related' % self.number
        cached = cache.get(cachekey)

        if cached is not None:
            return cached

        scored = defaultdict(list)
        related = []

        obj_tags = set(self.tags.values_list('name', flat=True))

        others = type(self).objects.exclude(
            pk=self.pk
        ).filter(
            published__lte=timezone.now()
        ).distinct().select_related().prefetch_related(
            'tags'
        )

        for other in others.distinct():
            score = 0
            other_tags = list(
                other.tags.values_list('name', flat=True)
            )

            other_tags = set(other_tags)
            for tag in other_tags:
                if tag in obj_tags:
                    score += 4

            if score:
                scored[score].append(other)

        for (score, posts) in sorted(
            scored.items(),
            key=lambda pair: pair[0]
        ):
            if score < 0:
                continue

            related.extend(
                sorted(
                    posts,
                    key=lambda post: post.published
                )
            )

        cached = list(reversed(related))[:5]
        cache.set(cachekey, cached, 60 * 60)
        return cached

    class Meta:
        ordering = ('-published',)
        get_latest_by = 'published'
