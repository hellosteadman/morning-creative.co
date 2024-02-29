from django.utils import html
from django.utils.dateformat import format as date
from markdown import markdown
from watson import search as watson


class EpisodeSearchAdapter(watson.SearchAdapter):
    def get_description(self, obj):
        return obj.get_excerpt()

    def get_content(self, obj):
        if not obj.body:
            return ''

        tags = list(obj.tags.values_list('name', flat=True))

        return '\n'.join(
            (
                html.strip_tags(markdown(obj.body)),
                ', '.join(sorted(set(tags)))
            )
        ).strip()

    def get_meta(self, obj):
        thumbnail = obj.thumbnail and obj.thumbnail.name or ''

        return {
            **super().get_meta(obj),
            'published': date(obj.published, 'F j, Y'),
            'thumbnail': thumbnail,
            'excerpt': obj.get_excerpt()
        }
