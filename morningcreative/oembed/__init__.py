from .helpers import get_html
from .rendering import RendererBase
from .registry import Library


default_app_config = 'morningcreative.oembed.apps.OembedConfig'
renderers = Library()


def register(domain):
    def wrapper(cls):
        renderers.register(domain, cls)
        return cls

    return wrapper


__all__ = (
    'get_html',
    'register',
    'RendererBase',
    'renderers'
)
