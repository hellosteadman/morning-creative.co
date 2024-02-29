from django.template import Library
from .. import get_html


register = Library()


@register.filter()
def oembed(value, width=None):
    kwargs = {}

    if width is not None:
        kwargs['width'] = width

    return get_html(value, **kwargs)
