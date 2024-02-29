from django.core.cache import cache
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from hashlib import md5
from mimetypes import guess_type
from urllib.parse import urljoin, urlparse, parse_qs
from xml.etree import ElementTree as ET
from . import renderers, settings
import json
import logging
import re
import requests


ATTR_REGEX = re.compile(
    r""" ([a-z]+)=(?:"([^"]+)"|'([^']+)')""",
    re.IGNORECASE
)

LINK_REGEX = re.compile(r'\<link[^\>]+\>', re.IGNORECASE)
LINK_TYPE_REGEX = re.compile(r'^application/(json|xml)\+oembed$')


def parse_oembed_response(response, fmt):
    if fmt == 'html' or fmt == 'callable':
        return response, None, None

    if fmt == 'json':
        data = json.loads(response)

        if 'html' in data:
            return (
                data.get('html'),
                data.get('title'),
                data.get('thumbnail_url')
            )

        return None, None, None

    xml = ET.fromstring(response)
    return (
        xml.find('html').text or '',
        xml.find('title').text or '',
        xml.find('thumbnail_url').text or ''
    )


def discover_html(url, format='full'):
    rendered = renderers.render_for_url(url)
    if rendered is not None:
        return rendered

    cachekey = '%s_%s' % (
        md5(url.encode('utf-8')).hexdigest(),
        format
    )

    response = cache.get(cachekey)
    if response is None:
        response = requests.get(
            url,
            headers={
                'User-Agent': settings.USER_AGENT
            },
            stream=True,
            allow_redirects=False
        )

        cache.set(cachekey, response, 60 * 60)

    try:
        response.raise_for_status()
    except Exception:
        logging.error('HTTP error discovering HTML', exc_info=True)
        return

    mimetype = response.headers.get('Content-Type')
    if (
        mimetype is None or (
            mimetype.startswith('text/html') and response.status_code > 201
        )
    ):
        mimetype, encoding = guess_type(
            urlparse(url).path
        )

        if not mimetype:
            mimetype = 'text/html'

    if mimetype.startswith('text/html') and format == 'full':
        matches = LINK_REGEX.findall(
            response.content.decode('utf-8')
        )

        for match in matches:
            attrs = {}
            for attr in ATTR_REGEX.findall(match):
                key, value1, value2 = attr
                attrs[key] = value1 or value2

            if attrs.get('rel') == 'alternate':
                fmt = LINK_TYPE_REGEX.match(attrs.get('type', ''))
                if fmt is not None:
                    fmt = fmt.groups()[0]
                    discovery_url = urljoin(url, attrs.get('href'))
                    urlparts = urlparse(discovery_url)
                    params = parse_qs(urlparts.query or urlparts.params)
                    q = discovery_url.find('?')

                    if q > -1:
                        discovery_url = discovery_url[:q]

                    oembed_response = requests.get(
                        discovery_url,
                        params=params,
                        headers={
                            'Accept': {
                                'json': 'application/json',
                                'xml': 'text/aml'
                            }[fmt],
                            'User-Agent': settings.USER_AGENT
                        }
                    )

                    if oembed_response.status_code >= 200:
                        if oembed_response.status_code < 400:
                            html, title, thumbnail_url = parse_oembed_response(
                                oembed_response.content.decode('utf-8'),
                                fmt
                            )

                            return mark_safe(html)

    elif mimetype.startswith('audio/'):
        return format_html(
            (
                '<audio src="{}" class="width-100" '
                'preload="none" controls></audio>'
            ),
            url
        )
    elif mimetype.startswith('video/'):
        return format_html(
            (
                '<video src="{}" class="width-100" '
                'preload="none" controls></video>'
            ),
            url
        )
    else:
        raise Exception(mimetype, url)

    return format_html(
        '<iframe src="{}" frameborder="0" width="100%"></iframe>',
        url
    )
