from dateutil.parser import parse as parse_date
from django.core.files import File
from django.db import models, transaction
from html2text import html2text
from markdown import markdown
from .helpers import download
import feedparser
import os
import requests


RSS_FEED_URL = 'https://feeds.transistor.fm/morning-creative'


class EpisodeQuerySet(models.QuerySet):
    @transaction.atomic
    def check_feed(self, logger=None):
        response = requests.get(
            RSS_FEED_URL,
            headers={
                'User-Agent': 'morningcreative.co/1'
            },
            stream=True
        )

        response.raise_for_status()
        feed = feedparser.parse(response.content)

        for entry in feed.entries:
            try:
                obj = self.get(
                    remote_id=entry.id
                )
            except self.model.DoesNotExist:
                obj = self.model(
                    remote_id=entry.id
                )

            obj.title = entry.title
            obj.published = parse_date(entry.published).date()
            obj.number = int(entry.itunes_episode)

            for content in entry.content:
                if content['type'] == 'text/html':
                    obj.body = html2text(
                        markdown(content['value']),
                        bodywidth=0
                    )

            for link in entry.links:
                if link['rel'] == 'enclosure':
                    obj.oembed = link['href']
                    break

            if hasattr(entry, 'bramble_embed'):
                obj.oembed = entry.bramble_embed['url']

            if entry.get('image') and (
                not obj.thumbnail or not os.path.exists(obj.thumbnail.path)
            ):
                thumbnail = download(entry.image['href'])
                obj.thumbnail = File(
                    open(thumbnail, 'rb'),
                    name='podcast/%s/thumbnail%s' % (
                        obj.number,
                        os.path.splitext(thumbnail)[-1]
                    )
                )

            obj.save()

            if callable(logger):
                logger(obj)
