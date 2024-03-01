from bs4 import BeautifulSoup
from django.utils import timezone
from django.views.generic import ListView, DetailView
from easy_thumbnails.files import get_thumbnailer
from html2text import html2text
from morningcreative import oembed
from morningcreative.seo.views import (
    SEOMixin,
    LinkedDataMixin,
    OpenGraphMixin,
    OpenGraphArticleMixin
)

from .models import Episode


class EpisodeMixin(SEOMixin, LinkedDataMixin):
    model = Episode

    def get_queryset(self):
        return super().get_queryset().select_related().prefetch_related(
            'tags'
        )


class EpisodeListView(OpenGraphMixin, EpisodeMixin, ListView):
    seo_title = 'Morning Creative episode archive'
    seo_description = (
        'Morning Creative is the daily podcast to help you reignite your '
        'spark and set yourself up for the day, motivated and energised.'
    )

    paginate_by = 12
    ld_type = 'PodcastSeries'

    def get_queryset(self):
        return super().get_queryset().filter(
            published__lte=timezone.now()
        )


class EpisodeDetailView(OpenGraphArticleMixin, EpisodeMixin, DetailView):
    ld_type = 'PodcastEpisode'
    slug_field = 'number'
    slug_url_kwarg = 'number'

    def get_seo_title(self):
        obj = self.get_object()
        return '%s – from Morning Creative' % obj.title

    def get_seo_description(self):
        obj = self.get_object()
        excerpt = obj.get_excerpt()
        return html2text(excerpt, bodywidth=0)

    def get_og_title(self):
        return self.get_object().title

    def get_og_description(self):
        obj = self.get_object()
        excerpt = obj.get_excerpt()
        return html2text(excerpt, bodywidth=0)

    def get_ld_attributes(self):
        obj = self.get_object()
        data = {
            'name': obj.title,
            'description': obj.get_excerpt(),
            'author': {
                '@type': 'Person',
                'name': 'Mark Steadman',
                'url': 'https://hellosteadman.com/'
            }
        }

        if obj.oembed:
            embed_url, embed_width, embed_height = None, None, None
            if embed_html := oembed.get_html(obj.oembed):
                if embed_soup := BeautifulSoup(embed_html, 'html.parser'):
                    if iframe := embed_soup.find('iframe'):
                        embed_url = iframe.get('src')
                        embed_width = iframe.get('width')
                        embed_height = iframe.get('height')

            data['associatedMedia'] = {
                '@type': 'MediaObject'
            }

            if embed_url:
                data['associatedMedia']['embedUrl'] = embed_url

            if embed_width:
                try:
                    data['associatedMedia']['width'] = int(embed_width)
                except ValueError:
                    pass

            if embed_height:
                try:
                    data['associatedMedia']['height'] = int(embed_height)
                except ValueError:
                    pass

        if obj.thumbnail:
            thumbnailer = get_thumbnailer(obj.thumbnail)
            thumbnail = thumbnailer.get_thumbnail(
                {
                    'size': (512, 512),
                    'crop': True
                }
            )

            data['thumbnailUrl'] = thumbnail.url

        data['isFamilyFriendly'] = True
        data['isSimilarTo'] = [
            self.request.build_absolute_uri(other.get_absolute_url())
            for other in obj.get_related_posts()
        ]

        return data

    def get_context_data(self, **kwargs):
        obj = self.get_object()

        return {
            'related_posts': obj.get_related_posts(),
            **super().get_context_data(**kwargs)
        }
