from django.db import models, transaction


class SubscriberQuerySet(models.QuerySet):
    @transaction.atomic
    def create_from_token(self, token):
        from .models import Unsubscriber
        from .tasks import welcome_subscriber

        name = token['n']
        email = token['e']
        timezone = token['z']
        created = False

        obj = self.filter(
            email__iexact=email
        ).first()

        if obj is None:
            obj = self.model(
                email=email.lower()
            )

            created = True

        obj.name = name or obj.name or ''
        obj.timezone = timezone
        obj.save()

        if created:
            transaction.on_commit(
                lambda: welcome_subscriber.delay(obj.pk)
            )

        Unsubscriber.objects.filter(
            email__iexact=obj.email
        ).delete()

        return obj
