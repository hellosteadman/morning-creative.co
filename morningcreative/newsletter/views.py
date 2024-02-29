from django.conf import settings
from django.http.response import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import (
    CreateView,
    TemplateView,
    FormView,
    View
)

from morningcreative.seo.views import SEOMixin

from .forms import (
    CreateSubscriberForm,
    ConfirmSubscriptionForm,
    UnsubscribeForm
)

from .models import Subscriber, Delivery
import jwt
import os


PODCASTS_MATCH = r'https?://podcasts\.apple\.com\/(\w+\/)?podcast\/(?:[\w-]+/)id(\d+)'  # NOQA


class CreateSubscriberView(SEOMixin, CreateView):
    form_class = CreateSubscriberForm
    model = Subscriber
    seo_title = 'Subscribe to the Morning Creative Journal Prompt'
    og_title = 'Add a daily dose of inspiration to your inbox'
    robots = 'noindex'

    def get_success_url(self):
        return reverse('subscriber_pending')


class ConfirmSubscriptionView(SEOMixin, CreateView):
    form_class = ConfirmSubscriptionForm
    model = Subscriber
    template_name = 'newsletter/confirm_subscription.html'
    seo_title = 'Confirm subscription'
    robots = 'noindex'

    def get_form_kwargs(self):
        try:
            token = jwt.decode(
                self.kwargs['token'],
                settings.SECRET_KEY,
                algorithms=('HS256',)
            )
        except jwt.exceptions.DecodeError:
            raise Http404()

        return {
            'token': token,
            **super().get_form_kwargs()
        }

    def get_success_url(self):
        return reverse('subscriber_created')

    def form_valid(self, form):
        response = super().form_valid(form)
        self.request.set_subscriber(self.object)
        return response


class SubscriptionPendingView(SEOMixin, TemplateView):
    template_name = 'newsletter/subscriber_pending.html'
    seo_title = 'Now check your inbox'
    robots = 'noindex'


class SubscriptionCreatedView(SEOMixin, TemplateView):
    template_name = 'newsletter/subscriber_created.html'
    seo_title = 'Subscription created'
    robots = 'noindex'


class DeliveryOpenTrackingView(View):
    def get(self, request, pk):
        obj = get_object_or_404(Delivery, pk=pk)

        if request.method == 'GET':
            obj.open(request)

        return HttpResponse(
            content_type='image/png',
            content=open(
                os.path.join(
                    os.path.dirname(__file__),
                    'fixtures',
                    'pixel.png'
                ),
                'rb'
            )
        )


class UnsubscribeView(SEOMixin, FormView):
    template_name = 'newsletter/unsubscribe_form.html'
    seo_title = 'Unsubscribe from Morning Creative'
    form_class = UnsubscribeForm
    robots = 'noindex'

    def form_valid(self, form):
        form.unsubscribe()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('unsubscriber_created')


class UnsubscriberCreatedView(SEOMixin, TemplateView):
    template_name = 'newsletter/unsubscriber_created.html'
    seo_title = 'Subscription created'
    robots = 'noindex'
