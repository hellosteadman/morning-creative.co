from django.conf import settings
from morningcreative.pages.models import Page
from urllib.parse import urlparse, urljoin


def main(request):
    cached = {}

    def first_visit():
        if 'first_visit' not in cached:
            if referrer := request.META.get('HTTP_REFERER'):
                current = request.build_absolute_uri()
                domain = urlparse(current).netloc

                try:
                    referrer = urljoin(current, referrer)
                except Exception:
                    cached['first_visit'] = True
                else:    
                    cached['first_visit'] = domain != urlparse(referrer).netloc
            else:
                cached['first_visit'] = True

        return cached['first_visit']

    return {
        'main_menu': [
            {
                'url': '/',
                'label': 'Home'
            },
            {
                'url': '/episodes/',
                'label': 'Episode archive'
            },
            {
                'url': '/prompt/',
                'label': 'Journal prompt'
            }
        ] + [
            {
                'url': page.get_absolute_url(),
                'label': page.name
            } for page in Page.objects.filter(
                menu_visibility=True
            )
        ],
        'DEBUG': settings.DEBUG,
        'first_visit': first_visit
    }
