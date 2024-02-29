from .handlers import HandlerBase
from .registry import Library
from .tags import ButtonHandler


default_app_config = 'morningcreative.miditags.apps.MiditagsConfig'
tags = Library()
tags.register('button', ButtonHandler)


def register(name):
    def wrapper(cls):
        tags.register(name, cls)
        return cls

    return wrapper


__all__ = (
    'HandlerBase',
    'tags',
    'register'
)
