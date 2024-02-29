from django.contrib import admin
from django.utils import timezone
from markdownx.admin import MarkdownxModelAdmin
from .models import Prompt


@admin.register(Prompt)
class PromptAdmin(MarkdownxModelAdmin):
    list_display = ('title', 'published')
    date_hierarchy = 'published'
    search_fields = ('title', 'body')

    def formfield_for_dbfield(self, field, *args, **kwargs):
        if field.name == 'published':
            date = timezone.now().date()
            while date.weekday() in (5, 6):
                date += timezone.timedelta(days=1)

            kwargs['initial'] = date

        return super().formfield_for_dbfield(field, *args, **kwargs)
