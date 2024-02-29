from datetime import datetime, timedelta
from django.db import models, transaction
from .tasks import email_sponsorship
import re


MESSAGE_LINK_EX = r'\[([^\[]+)\]'


class SponsorshipQuerySet(models.QuerySet):
    @transaction.atomic
    def create_from_checkout(self, session):
        from morningcreative.newsletter.models import Subscriber
        from .models import Sponsor

        customer_details = session.customer_details
        sponsorship_details = session.metadata

        with transaction.atomic():
            sponsor = Sponsor.objects.select_for_update().filter(
                email__iexact=customer_details['email']
            ).first()

            if sponsor is None:
                sponsor = Sponsor(
                    email=customer_details['email'].lower()
                )

            sponsor.name = (
                customer_details['name'] or
                sponsorship_details['name'] or
                sponsor.name
            )

            sponsor.save()

        with transaction.atomic():
            subscriber = Subscriber.objects.select_for_update().filter(
                email__iexact=customer_details['email']
            ).first()

            if subscriber is None:
                subscriber = Subscriber(
                    email=customer_details['email'].lower()
                )

            subscriber.name = (
                customer_details['name'] or
                sponsor.name or
                subscriber.name
            )

            subscriber.save()

        start = datetime.strptime(sponsorship_details['issue'], '%Y-%m-%d')
        end = start + timedelta(days=6)
        message = re.sub(
            MESSAGE_LINK_EX,
            r'[\g<1>](%s)' % sponsorship_details['url'],
            sponsorship_details['message']
        )

        obj = self.create(
            sponsor=sponsor,
            start=start,
            end=end,
            price=session.amount_total / 100,
            stripe_id=session.payment_intent,
            message=message
        )

        transaction.on_commit(
            lambda: email_sponsorship.delay(obj.pk)
        )

        return obj
