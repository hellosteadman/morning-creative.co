from django.db import models
from easy_thumbnails.fields import ThumbnailerImageField
from markdownx.models import MarkdownxField
import os


class Page(models.Model):
    def upload_header(self, filename):
        return 'pages/%s/header%s' % (
            self.slug,
            os.path.splitext(filename)[-1]
        )

    name = models.CharField(max_length=50)
    headline = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(max_length=100, unique=True)
    header = ThumbnailerImageField(
        upload_to=upload_header,
        max_length=255,
        null=True,
        blank=True
    )

    oembed = models.URLField(
        'oEmbed URL',
        max_length=255,
        null=True,
        blank=True
    )

    body = MarkdownxField(null=True, blank=True)
    menu_visibility = models.BooleanField(default=True)
    menu_order = models.PositiveIntegerField(default=0)

    seo_title = models.CharField(
        'SEO title',
        max_length=255,
        null=True,
        blank=True
    )

    seo_description = models.TextField(
        'SEO description',
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return '/%s/' % self.slug

    class Meta:
        ordering = ('menu_order',)
