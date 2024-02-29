from django.contrib.sitemaps import Sitemap
from django.utils import timezone
from .models import Episode


class EpisodeSitemap(Sitemap):
    changefreq = 'monthly'

    def items(self):
        return Episode.objects.filter(
            published__lte=timezone.now()
        ).prefetch_related(
            'tags'
        ).select_related().order_by(
            '-published'
        )

    def lastmod(self, obj):
        return obj.published

    def priority(self, obj):
        value = 0
        if obj.price:
            value += float(obj.price) / 120

        value -= .2
        value = max(.1, min(1, value))
        return round(value, 1)
