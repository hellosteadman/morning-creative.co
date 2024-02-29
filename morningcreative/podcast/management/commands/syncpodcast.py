from django.core.management.base import BaseCommand
from morningcreative.podcast.models import Episode


class Command(BaseCommand):
    help = 'Sync with podcast feed'

    def handle(self, *args, **options):
        Episode.objects.check_feed(print)
