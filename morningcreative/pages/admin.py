from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin
from .models import Page


@admin.register(Page)
class PageAdmin(MarkdownxModelAdmin):
    list_display = ('name',)
    prepopulated_fields = {
        'slug': ('name',)
    }
