from django.template import Library
from urllib.parse import urlsplit, parse_qs, urlencode, urlunsplit
import re


MARKDOWN_LINK_REGEX = r'\[([^\]]+)\]\(([^\)]+)\)'


register = Library()


def get_destination_url(url, campaign=None):
    scheme, location, path, query, fragment = urlsplit(url)
    query = parse_qs(query)

    if 'utm_source' not in query:
        query['utm_source'] = 'morningcreative'

    if 'utm_medium' not in query:
        query['utm_medium'] = 'web'

    if campaign and 'utm_campaign' not in query:
        query['utm_campaign'] = campaign

    query = urlencode(query, doseq=True)
    return urlunsplit((scheme, location, path, query, fragment))


@register.filter()
def utmlinks(value, campaign=None):
    def replacer(match):
        inner, href = match.groups()
        if (
            href.startswith('mailto:') or
            href.startswith('#') or
            href.startswith('javascript:') or
            (
                href.startswith('/') and
                not href.startswith('//')
            )
        ):
            return '<%s>' % href

        return '[%s](%s)' % (
            inner,
            get_destination_url(href, campaign)
        )

    return re.sub(MARKDOWN_LINK_REGEX, replacer, value)
