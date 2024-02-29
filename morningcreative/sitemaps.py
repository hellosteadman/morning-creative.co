from django.contrib.sitemaps.views import sitemap, index
from django.urls import path
from .podcast.sitemaps import EpisodeSitemap


sitemaps = {
    'episodes': EpisodeSitemap
}

urlpatterns = [
    path(
        'sitemap.xml',
        index,
        {
            'sitemaps': sitemaps
        },
        name='django.contrib.sitemaps.views.index'
    ),
    path(
        'sitemap-<section>.xml',
        sitemap,
        {
            'sitemaps': sitemaps
        },
        name='django.contrib.sitemaps.views.sitemap'
    )
]
