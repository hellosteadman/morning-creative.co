from django import forms
from django.conf import settings
from django.db import transaction
from django.urls import reverse
from hashlib import sha256
from morningcreative.mail.tasks import send_email
from .helpers import random_phrase
from .models import Subscriber, Unsubscriber
import jwt
import pytz
import re


class ImportSubscribersForm(forms.Form):
    emails = forms.CharField(
        label='Email addresses',
        widget=forms.Textarea,
        help_text=(
            'Add each email address on a separate line. '
            'You can use "Name &lt;email&gt;" formatting too, to import '
            'a subscriber with a full name.'
        )
    )

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)

    def clean_emails(self):
        lines = self.cleaned_data['emails'].splitlines()
        clean_lines = []
        emails = {}

        for i, line in enumerate(lines):
            if not line and not line.strip():
                continue

            if re.match(r'^ *[^@<]+@[^@]+\.[^@]+ *$', line):
                email = line.strip()
                clean_lines.append(email)
                name = ''
            else:
                match = re.match(
                    r'^([^<]+) *< *([^@]+@[^@]+\.[^@]+) *> *$',
                    line
                )

                if match is None:
                    raise forms.ValidationError(
                        'Line %d contains a malformed address.' % (i + 1)
                    )

                name, email = [g.strip() for g in match.groups()]
                clean_lines.append(
                    '%s <%s>' % (name, email)
                )

            if email.lower() in emails:
                raise forms.ValidationError(
                    (
                        'Line %d contains an email address already being '
                        'imported.' % (i + 1)
                    )
                )

            emails[email.lower()] = name

        self.__emails = emails
        return '\n'.join(
            set(clean_lines)
        )

    def save(self, commit=True):
        emails = self.__emails
        subscriber = None

        for email, name in emails.items():
            subscriber, created = Subscriber.objects.get_or_create(
                email=email.lower(),
                defaults={
                    'name': name
                }
            )

        return subscriber

    def save_m2m(self):
        pass


class CreateSubscriberForm(forms.Form):
    email = forms.EmailField(
        label='Enter your email address',
        max_length=255,
        widget=forms.EmailInput(
            attrs={
                'placeholder': 'jo@bloggs.com',
                'class': 'form-control-lg'
            }
        )
    )

    name = forms.CharField(
        label='And your name',
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Jo Bloggs'
            }
        )
    )

    timezone = forms.ChoiceField(
        label='Timezone',
        widget=forms.HiddenInput(),
        initial=settings.TIME_ZONE,
        choices=[
            (z, z.replace('_', ' '))
            for z in sorted(pytz.common_timezones_set)
        ]
    )

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        for subscriber in Subscriber.objects.filter(
            email__iexact=self.cleaned_data['email']
        ):
            return True

        phrase = random_phrase()
        hashed_phrase = sha256(phrase.encode('utf-8')).hexdigest()
        params = {
            'n': self.cleaned_data['name'] or '',
            'e': self.cleaned_data['email'].lower(),
            'p': hashed_phrase,
            'z': self.cleaned_data['timezone']
        }

        token = jwt.encode(
            params,
            settings.SECRET_KEY,
            algorithm='HS256'
        )

        send_email.delay(
            'Confirm your subscription to the Morning Creative Journal Prompt',
            'newsletter/confirm_subscription_email.md',
            {
                'title': 'Confirm your subscription',
                'url': 'http%s://%s%s' % (
                    not settings.DEBUG and 's' or '',
                    settings.DOMAIN,
                    reverse('confirm_subscription', args=(token,))
                ),
                'phrase': phrase
            },
            (
                self.cleaned_data['name'] or '',
                self.cleaned_data['email']
            ),
            html_template='newsletter/confirm_subscription_email.html'
        )

        return False


class MiniCreateSubscriberForm(CreateSubscriberForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['class'] = ''


class ConfirmSubscriptionForm(forms.Form):
    phrase = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control-lg',
                'autofocus': True
            }
        )
    )

    def __init__(self, *args, **kwargs):
        self.token = kwargs.pop('token')
        self.instance = kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)

    def clean_phrase(self):
        phrase = self.cleaned_data['phrase'].lower().strip()
        hashed_phrase = sha256(phrase.encode('utf-8')).hexdigest()

        if hashed_phrase != self.token['p']:
            raise forms.ValidationError(
                'Please enter the phrase as specified in the email.'
            )

        return self.cleaned_data['phrase']

    def save(self, commit=True):
        return Subscriber.objects.create_from_token(self.token)


class UnsubscribeForm(forms.Form):
    email = forms.EmailField()

    @transaction.atomic
    def unsubscribe(self):
        for obj in Unsubscriber.objects.filter(
            email__iexact=self.cleaned_data['email']
        ):
            return obj

        for obj in Subscriber.objects.filter(
            email__iexact=self.cleaned_data['email']
        ):
            return Unsubscriber.objects.create(
                email=self.cleaned_data['email'].lower()
            )
