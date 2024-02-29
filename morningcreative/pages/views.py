from django.views.generic import DetailView
from easy_thumbnails.files import get_thumbnailer
from morningcreative.seo.views import (
    SEOMixin,
    OpenGraphArticleMixin,
    LinkedDataMixin
)

from .models import Page


class PageDetailView(
    SEOMixin, OpenGraphArticleMixin, LinkedDataMixin, DetailView
):
    model = Page
    ld_type = 'WebPage'

    def get_seo_title(self):
        obj = self.get_object()
        return obj.seo_title or obj.headline or obj.name

    def get_seo_description(self):
        obj = self.get_object()
        return obj.seo_description

    def get_robots(self):
        obj = self.get_object()

        if not obj.menu_visibility:
            return 'noindex'

        return super().get_robots()

    def get_ld_attributes(self):
        obj = self.get_object()
        data = {
            'name': obj.name,
            'description': obj.headline or '',
            'author': {
                '@type': 'Person',
                'name': 'Mark Steadman',
                'url': self.request.build_absolute_uri('/')
            }
        }

        if obj.header:
            thumbnailer = get_thumbnailer(obj.header)
            thumbnail = thumbnailer.get_thumbnail(
                {
                    'size': (512, 512),
                    'crop': True
                }
            )

            data['thumbnailUrl'] = thumbnail.url

        return data
