from django.utils import html
from markdown import markdown
from watson import search as watson


class PageSearchAdapter(watson.SearchAdapter):
    def get_description(self, obj):
        return obj.headline or ''

    def get_content(self, obj):
        return html.strip_tags(markdown(obj.body))

    def get_meta(self, obj):
        return {
            **super().get_meta(obj),
            'thumbnail': obj.header and obj.header.name or ''
        }
