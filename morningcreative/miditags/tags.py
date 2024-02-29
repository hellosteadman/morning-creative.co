from django.utils.html import format_html
from .handlers import HandlerBase


class ButtonHandler(HandlerBase):
    def handle(self, text, url, **kwargs):
        background = kwargs.get('background', 'primary')
        size = kwargs.get('size', 'medium')
        full_width = kwargs.get('fullwidth', True)
        external = kwargs.get('external')
        classes = ['btn']

        if external is None:
            if url.startswith('//'):
                external = True
            elif url.startswith('/'):
                external = False
            else:
                external = True

        if size in ('sm', 'lg'):
            classes.append('btn-%s' % size)

        classes.append('btn-%s' % background)

        if full_width:
            classes.extend(
                (
                    'width-100',
                    'shadow-lg',
                    'margin-y-4'
                )
            )

        return format_html(
            '<a href="{}"{} class="{}">{}</a>',
            url,
            external and ' target="_blank"' or '',
            ' '.join(classes),
            text
        )
