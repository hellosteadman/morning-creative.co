from django.db import models
from markdownx.models import MarkdownxField


class Prompt(models.Model):
    published = models.DateField()
    title = models.CharField(max_length=140)
    body = MarkdownxField(null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('-published',)
        get_latest_by = 'published'
