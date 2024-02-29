from django.apps import AppConfig
from watson import search as watson
from .search import PageSearchAdapter


class PagesConfig(AppConfig):
    name = 'morningcreative.pages'

    def ready(self):
        Page = self.get_model('Page')
        watson.register(Page, PageSearchAdapter)
