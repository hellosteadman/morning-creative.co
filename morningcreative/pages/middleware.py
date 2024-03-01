from .models import Page
from .views import PageDetailView


def pages_middleware(get_response):
    def middleware(request):
        slugs = [part for part in request.path.split('/') if part]
        response = get_response(request)

        if response.status_code == 404:
            if len(slugs) == 1:
                for page in Page.objects.filter(slug=slugs[0]):
                    view = PageDetailView.as_view()
                    response = view(request, slug=page.slug)
                    return response.render()

        return response

    return middleware
