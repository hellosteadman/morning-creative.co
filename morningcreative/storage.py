from django.contrib.staticfiles.storage import StaticFilesStorage
import os


class LocalNetworkStorage(StaticFilesStorage):
    def url(self, name):
        url = super().url(name)
        static_url = os.getenv('STATIC_URL', '/static/')

        if not static_url.endswith('/'):
            static_url += '/'

        if url.startswith('/static/'):
            url = static_url + url[8:]

        return url
