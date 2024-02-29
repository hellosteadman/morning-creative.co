from django.conf import settings
from django.template import Library
from django.utils.safestring import mark_safe
from markdown import markdown as md
import bleach


register = Library()


@register.filter()
def markdown(value, style='default'):
    cleaned = bleach.clean(str(value))
    kwargs = settings.MARKDOWN_STYLES.get(style, {})
    kwargs.update(
        {
            'output_format': 'html'
        }
    )

    if cleaned and str(cleaned).strip():
        return mark_safe(
            md(
                str(cleaned),
                **kwargs
            )
        )

    return ''
