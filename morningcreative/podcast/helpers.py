from django.db import transaction
from mimetypes import guess_extension
from PIL import Image, UnidentifiedImageError
from tempfile import mkstemp
from urllib.parse import urlparse
import imagehash
import os
import requests


def fix_weird_download(response):
    path = urlparse(response.request.url).path
    if path.endswith('.flac'):
        handle, filename = mkstemp('.flac')

        try:
            for chunk in response.iter_content(chunk_size=1024*1024):
                os.write(handle, chunk)
        finally:
            os.close(handle)

        return filename

    try:
        image = Image.open(response.raw)
    except UnidentifiedImageError:
        raise Exception(response.request.url)
    else:
        if image.format == 'JPEG':
            handle, filename = mkstemp('.jpg')
            os.close(handle)
            image.save(filename)
            return filename

        raise Exception(image.format)


def download(url):
    response = requests.get(url, stream=True)
    response.raise_for_status()
    content_type = response.headers['Content-Type']

    if content_type == 'application/octet-stream':
        filename = fix_weird_download(response)
        transaction.on_commit(
            lambda: os.remove(filename)
        )

        return filename

    ext = guess_extension(content_type)
    handle, filename = mkstemp(ext)

    try:
        for chunk in response.iter_content(chunk_size=1024*1024):
            os.write(handle, chunk)
    finally:
        os.close(handle)

    transaction.on_commit(
        lambda: os.remove(filename)
    )

    return filename


def compare_image(a, b):
    original_hash = imagehash.average_hash(Image.open(a))
    comparison_hash = imagehash.average_hash(Image.open(b))

    return (comparison_hash - original_hash)
