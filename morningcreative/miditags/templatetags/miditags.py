from django.conf import settings
from django.template import Library
from django.utils.safestring import mark_safe
from markdown import markdown as md
import bleach
from .. import tags


register = Library()


@register.simple_tag(takes_context=True)
def miditags(context, value, format='full'):
    if not value:
        return ''

    lines = []
    quote = []

    for line in value.splitlines():
        if line.startswith('> '):
            quote.append(line)
        elif any(quote):
            lines.append(
                md('\n'.join(quote))
            )

            quote = []
        else:
            lines.append(line)

    cleaned = bleach.clean(
        '\n'.join(lines),
        tags=(
            'a',
            'b',
            'br',
            'blockquote',
            'cite',
            'code',
            'del',
            'em',
            'h1',
            'h2',
            'h3',
            'h4',
            'h5',
            'h6',
            'hr',
            'i',
            'img',
            'ins',
            'li',
            'ol',
            'p',
            'pre',
            'q',
            'span',
            'strike',
            'strong',
            'ul'
        ),
        attributes={
            'a': ('href', 'target', 'download', 'rel'),
            'img': ('alt', 'src')
        }
    )

    plain = tags.parse(
        cleaned,
        format,
        base_context={
            'object': context.get('object')
        }
    )

    kwargs = settings.MARKDOWN_STYLES.get('default', {})
    kwargs.update(
        {
            'output_format': 'html'
        }
    )

    return mark_safe(
        md(plain, **kwargs)
    )
