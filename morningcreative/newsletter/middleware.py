from django.conf import settings
from .models import Subscriber


def subscriber_middleware(get_response):
    def middleware(request):
        def set_subscriber(subscriber):
            if subscriber is not None:
                request.session['subscriber_id'] = str(subscriber.pk)
            else:
                request.session.pop('subscriber_id')

            request.session.modified = True

            if subscriber is not None:
                subscriber.set_active(request, force=True)

        if settings.DEBUG:
            if (
                request.path.startswith('/media/') or
                request.path.startswith('/static/')
            ):
                return get_response(request)

        request.set_subscriber = set_subscriber
        subscriber_id = request.session.get('subscriber_id')

        if subscriber_id is not None:
            request.subscriber = Subscriber.objects.filter(
                pk=subscriber_id
            ).first()

            if request.subscriber is not None:
                request.subscriber.set_active(request)
        else:
            request.subscriber = None

        return get_response(request)

    return middleware
