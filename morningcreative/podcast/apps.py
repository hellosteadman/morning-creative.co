from django.apps import AppConfig
from watson import search as watson
from .search import EpisodeSearchAdapter


class PodcastConfig(AppConfig):
    name = 'morningcreative.podcast'

    def ready(self):
        Episode = self.get_model('Episode')
        watson.register(
            Episode.objects.exclude(published=None),
            EpisodeSearchAdapter
        )
