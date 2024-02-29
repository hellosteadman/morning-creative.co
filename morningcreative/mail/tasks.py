from django_rq.decorators import job
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from email.utils import formataddr
import os


@job('default', timeout='1m')
def send_email(
    subject,
    body_template,
    body_context,
    recipient,
    html_template=None,
    unsubscribe_url=None,
    tracking_pixel_url=None
):
    base_context = {
        'sender': {
            'name': settings.DEFAULT_FROM_NAME,
            'email': settings.DEFAULT_FROM_EMAIL
        },
        'base_url': 'http%s://%s' % (
            not settings.DEBUG and 's' or '',
            settings.DOMAIN
        ),
        'body_font': (
            "-apple-system, "
            "BlinkMacSystemFont, "
            "'Segoe UI', "
            "Roboto, "
            "Helvetica, "
            "Arial, "
            "sans-serif, "
            "'Apple Color Emoji', "
            "'Segoe UI Emoji', "
            "'Segoe UI Symbol'"
        )
    }

    if unsubscribe_url:
        base_context['unsubscribe_url'] = 'http%s://%s%s' % (
            not settings.DEBUG and 's' or '',
            settings.DOMAIN,
            unsubscribe_url
        )

    if tracking_pixel_url:
        base_context['tracking_pixel_url'] = 'http%s://%s%s' % (
            not settings.DEBUG and 's' or '',
            settings.DOMAIN,
            tracking_pixel_url
        )

    if isinstance(recipient, tuple) and len(recipient) == 2:
        recipient = formataddr(recipient)

    message = EmailMultiAlternatives(
        subject,
        render_to_string(
            'mail/base.md',
            {
                'body': render_to_string(
                    body_template,
                    body_context
                ),
                **base_context
            }
        ),
        formataddr(
            (
                settings.DEFAULT_FROM_NAME,
                settings.DEFAULT_FROM_EMAIL
            )
        ),
        [recipient]
    )

    if html_template:
        body = render_to_string(
            html_template,
            {
                **body_context,
                **base_context
            }
        )
    else:
        body = render_to_string(
            'mail/email_body.html',
            {
                'body': render_to_string(
                    body_template,
                    {
                        **body_context,
                        **base_context
                    }
                ),
                **body_context
            }
        )

    message.attach_alternative(
        render_to_string(
            'mail/base.html',
            {
                'body': body,
                'css': mark_safe(
                    open(
                        os.path.join(
                            os.path.dirname(__file__),
                            'fixtures',
                            'email.css'
                        )
                    ).read()
                ),
                **base_context
            }
        ),
        'text/html'
    )

    message.send()
