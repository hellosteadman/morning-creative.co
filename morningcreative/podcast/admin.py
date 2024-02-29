from django.contrib import admin
from django.utils import timezone
from markdownx.admin import MarkdownxModelAdmin
from .models import Episode


@admin.register(Episode)
class EpisodeAdmin(MarkdownxModelAdmin):
    list_display = ('title', 'number', 'published')
    date_hierarchy = 'published'
    search_fields = ('title', 'body', 'tags__name')

    fieldsets = (
        (
            None,
            {
                'fields': ('title',)
            }
        ),
        (
            'Media',
            {
                'fields': (
                    'thumbnail',
                    'poster',
                    'oembed'
                )
            }
        ),
        (
            'Content',
            {
                'fields': ('body',)
            }
        ),
        (
            'Taxonomy',
            {
                'fields': ('tags',)
            }
        ),
        (
            'Meta',
            {
                'fields': (
                    'number',
                    'published',
                    'excerpt'
                ),
                'classes': ('collapse',)
            }
        )
    )

    def formfield_for_dbfield(self, field, *args, **kwargs):
        if field.name == 'number':
            if obj := Episode.objects.order_by('-number').first():
                kwargs['initial'] = obj.number + 1
            else:
                kwargs['initial'] = 1
        elif field.name == 'published':
            date = timezone.now().date()
            while date.weekday() in (5, 6):
                date += timezone.timedelta(days=1)

            kwargs['initial'] = date

        return super().formfield_for_dbfield(field, *args, **kwargs)
