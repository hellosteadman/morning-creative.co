from django.core.cache import cache
from django.template import Template, Context
from django.utils.html import format_html
from hashlib import md5
from . import settings
import re


def get_html(url, width=696, height=392, format='full', discover=True):
    size = '%dx%x' % (width, height)

    for provider in settings.EMBED_PROVIDERS:
        for pattern in provider['patterns']:
            compiled = re.compile(pattern)
            match = compiled.match(url)

            if match is not None:
                groups = match.groups()
                context = Context(
                    {
                        'url': url,
                        'width': width,
                        'height': height,
                        'params': groups
                    }
                )

                template = Template(provider['html'])
                return template.render(context)

    if not discover:
        return

    from . import utils

    cachekey = md5(
        ('embed_%s_%s' % (url, size)).encode('utf-8')
    ).hexdigest()
    cached = cache.get(cachekey)

    if cached is None:
        cached = utils.discover_html(url)

        if cached is not None:
            cache.set(cachekey, cached, 60 * 60 * 24)

    return cached or format_html(
        (
            '<iframe src="{}" frameborder="0" width="100%"></iframe>'
        ),
        url
    )
