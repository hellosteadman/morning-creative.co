from django.utils import timezone
from django.views.generic import DetailView
from morningcreative.newsletter.forms import CreateSubscriberForm
from morningcreative.podcast.models import Episode
from morningcreative.seo.views import SEOMixin
from .models import Prompt


class LatestPromptView(SEOMixin, DetailView):
    def get_seo_title(self):
        return 'Daily prompt for your creative journal'

    def get_seo_description(self):
        return (
            'Check back each weekday for a prompt or provocation '
            'to aid you in your creative practice.'
        )

    def get_object(self):
        return Prompt.objects.filter(
            published__lte=timezone.now().date()
        ).latest()

    def get_context_data(self, **kwargs):
        obj = self.get_object()

        return {
            'episode': Episode.objects.filter(
                published=obj.published
            ).first(),
            'subscribe_form': CreateSubscriberForm(),
            **super().get_context_data(**kwargs)
        }
