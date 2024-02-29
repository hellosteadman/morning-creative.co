from django.db import models
from django.utils import html, functional
from markdownx.models import MarkdownxField
from markdown import markdown
from .query import SponsorshipQuerySet
import re


MARKDOWN_LINK_REGEX = r'\[[^\]]+\]\(([^\)]+)\)'


class Sponsor(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=255, null=True, blank=True)
    stripe_id = models.CharField(
        'Stripe ID',
        max_length=64,
        null=True,
        editable=False
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)


class Sponsorship(models.Model):
    objects = SponsorshipQuerySet.as_manager()

    sponsor = models.ForeignKey(
        Sponsor,
        related_name='sponsorships',
        on_delete=models.CASCADE
    )

    message = MarkdownxField()
    start = models.DateField(null=True, blank=True)
    end = models.DateField(null=True, blank=True)
    price = models.DecimalField(
        decimal_places=2,
        max_digits=6,
        null=True,
        blank=True
    )

    stripe_id = models.CharField(
        'Stripe ID',
        max_length=64,
        null=True,
        editable=False
    )

    def __str__(self):
        return html.strip_tags(
            markdown(self.message.split('. ')[0])
        )

    @functional.cached_property
    def url(self):
        match = re.search(MARKDOWN_LINK_REGEX, self.message)
        if match is not None:
            return match.groups()[0]

    class Meta:
        ordering = ('-start', 'sponsor__name')


class Announcement(models.Model):
    body = MarkdownxField()
    date = models.DateField()

    def __str__(self):
        return html.strip_tags(
            markdown(self.body.split('. ')[0])
        )

    class Meta:
        ordering = ('-date',)
