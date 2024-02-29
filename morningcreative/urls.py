from django.conf import settings
from django.contrib import admin
from django.urls import path, re_path, include
from django.views.defaults import page_not_found, server_error
from django.views.generic.base import TemplateView
from .views import SearchEntryListView
from . import sitemaps


handler404 = 'morningcreative.views.handler_404'
urlpatterns = (
    path('admin/markdownx/', include('markdownx.urls')),
    path('admin/rq/', include('django_rq.urls')),
    path('admin/', admin.site.urls),
    path('prompt/', include('morningcreative.prompts.urls')),
    path('~/', include('morningcreative.oembed.urls')),
    path('search/', SearchEntryListView.as_view(), name='search_entry_list'),
    path('', include(sitemaps))
)

if settings.DEBUG:
    from django.views.static import serve as static_serve

    urlpatterns += (
        re_path(
            r'^media/(?P<path>.*)$',
            static_serve,
            {
                'document_root': settings.MEDIA_ROOT
            }
        ),
        path(
            '404.html',
            page_not_found,
            {
                'exception': Exception()
            }
        ),
        path(
            '500.html',
            server_error
        ),
        path(
            '503.html',
            TemplateView.as_view(
                template_name='503.html'
            )
        )
    )


urlpatterns += (
    path('', include('morningcreative.analytics.urls')),
    path('', include('morningcreative.newsletter.urls')),
    path('', include('morningcreative.podcast.urls')),
)
