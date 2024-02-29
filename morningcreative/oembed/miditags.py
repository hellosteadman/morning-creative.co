from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from morningcreative import miditags
import jwt


@miditags.register('embed')
class EmbedHandler(miditags.HandlerBase):
    def handle(self, url, discover=True):
        return render_to_string(
            'oembed/oembed_filter.html',
            {
                'token': jwt.encode(
                    {
                        'u': url,
                        'd': discover and 1 or 0,
                        'exp': timezone.now() + timezone.timedelta(minutes=1)
                    },
                    settings.SECRET_KEY,
                    algorithm='HS256'
                )
            }
        )
