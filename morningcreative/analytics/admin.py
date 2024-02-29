from django.contrib import admin
from django.db.models import Count, Sum
from .models import TrackedLink, TrackedLinkClick


class TrackedLinkClickInline(admin.TabularInline):
    model = TrackedLinkClick

    def has_add_permission(self, request, parent):
        return False

    def has_delete_permission(self, request, parent, obj=None):
        return False

    def has_change_permission(self, request, parent, obj=None):
        return False


@admin.register(TrackedLink)
class TrackedLinkAdmin(admin.ModelAdmin):
    list_display = ('url', 'text', 'clicks_unique', 'clicks_total')
    inlines = (TrackedLinkClickInline,)

    def clicks_unique(self, obj):
        return obj.clicks_unique or 0

    def clicks_total(self, obj):
        return obj.clicks_total or 0

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            clicks_unique=Count('clicks'),
            clicks_total=Sum('clicks__clicks')
        )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
