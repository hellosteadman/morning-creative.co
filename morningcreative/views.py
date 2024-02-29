from django.http.response import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.views.generic import ListView
from morningcreative.seo.views import SEOMixin
from urllib.parse import urlencode
from watson.search import search
import re


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

    slugs = request.path.split('/')[1:-1]
    slugs = re.split(r'/|-', request.path)
    query = ' '.join([slug for slug in slugs if slug])
    results = search(query)

    if results.count() == 1:
        result = results[0]
        if result.meta and (permalink := result.meta.get('permalink')):
            return HttpResponseRedirect(permalink)

        return HttpResponseRedirect(result.get_absolute_url())

    return TemplateResponse(
        request,
        '404.html',
        {
            'search_results': results
        },
        status=404
    )
