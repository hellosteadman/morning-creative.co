from django.http.response import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.utils import timezone
from django.views.generic import TemplateView, ListView
from morningcreative.podcast.models import Episode
from morningcreative.seo.views import SEOMixin
from urllib.parse import urlencode
from watson.search import search
import re


class HomepageView(SEOMixin, TemplateView):
    seo_title = 'Morning Creative – Daily podcast for creative wellbeing'
    seo_description = (
        'Morning Creative is the daily podcast for imaginative thinkers '
        'and doers working on their Big Project. Each 20-minute episode '
        'mixes prompts, gentle provocations, and practical actions you can '
        'take today to further your practice.'
    )

    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        return {
            'episode_list': Episode.objects.filter(
                published__lte=timezone.now().date()
            ),
            **super().get_context_data(**kwargs)
        }


class SearchEntryListView(SEOMixin, ListView):
    robots = 'noindex'
    paginate_by = 36

    def get_queryset(self):
        return search(
            self.request.GET.get('q', '')
        )

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'q': self.request.GET.get('q', '')
        }

    def get_canonical_url(self):
        params = {
            'q': self.request.GET.get('q', '')
        }

        if page := self.request.GET.get('page'):
            try:
                page = int(page)

                if page > 1:
                    params['page'] = page
            except Exception:
                print('Invalid page')

        return self.request.build_absolute_uri(
            '%s?%s' % (
                self.request.path,
                urlencode(params)
            )
        )


def handler_404(request, exception):
    if not request.path.endswith('/'):
        path = request.path + '/'
        if request.META.get('QUERY_STRING'):
            path += '?' + request.META['QUERY_STRING']

        return HttpResponseRedirect(path)

    return TemplateResponse(
        request,
        '404.html',
        status=404
    )
