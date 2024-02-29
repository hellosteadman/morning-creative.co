from django.contrib import admin
from django.utils import timezone
from markdownx.admin import MarkdownxModelAdmin
from .models import Sponsor, Sponsorship, Announcement


@admin.register(Sponsor)
class SponsorAdmin(MarkdownxModelAdmin):
    list_display = ('name',)


@admin.register(Sponsorship)
class SponsorshipAdmin(MarkdownxModelAdmin):
    list_display = ('__str__', 'sponsor', 'start')
    list_filter = ('start', 'sponsor')
    date_hierarchy = 'start'


@admin.register(Announcement)
class AnnouncementAdmin(MarkdownxModelAdmin):
    list_display = ('__str__', 'date')
    date_hierarchy = 'date'

    def formfield_for_dbfield(self, field, request, **kwargs):
        if field.name == 'date':
            kwargs['initial'] = timezone.now().date()

        return super().formfield_for_dbfield(field, request, **kwargs)
