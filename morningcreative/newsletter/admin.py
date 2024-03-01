from django.contrib import admin, messages
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Q
from django.http.response import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils import timezone, html
from functools import update_wrapper
from markdownx.admin import MarkdownxModelAdmin
from morningcreative.podcast.models import Episode
from morningcreative.prompts.models import Prompt
from .forms import ImportSubscribersForm
from .models import Post, Subscriber, Unsubscriber


@admin.register(Post)
class PostAdmin(MarkdownxModelAdmin):
    list_display = (
        'title',
        'published',
        'delivery_count',
        'open_rate'
    )

    search_fields = ('title', 'body')
    date_hierarchy = 'published'
    fields = (
        'title',
        'prompt',
        'episode',
        'body',
        'sponsorship',
        'published'
    )

    def delivery_count(self, obj):
        return obj.delivery_count or None

    def open_rate(self, obj):
        if obj.delivery_count and obj.open_count:
            return '%d%%' % int(obj.open_count / obj.delivery_count * 100)

        return 0 if obj.delivery_count else None

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            delivery_count=Count(
                'deliveries',
                filter=Q(deliveries__delivered__isnull=False),
                distinct=True
            ),
            open_count=Count(
                'deliveries__opens__delivery_id',
                filter=Q(deliveries__opens__score__gte=0),
                distinct=True
            )
        )

    def get_urls(self):
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.model_name
        urls = super().get_urls()

        return [
            path(
                '<path:object_id>/test/',
                wrap(self.test_view),
                name='%s_%s_test' % info
            ),
            path(
                '<path:object_id>/schedule/',
                wrap(self.schedule_view),
                name='%s_%s_schedule' % info
            )
        ] + urls

    def test_view(self, request, object_id, extra_context=None):
        opts = self.model._meta
        obj = self.get_object(request, admin.utils.unquote(object_id))
        obj.send_test_delivery(request.user.email)

        obj_url = reverse(
            'admin:%s_%s_change' % (opts.app_label, opts.model_name),
            args=(admin.utils.quote(object_id),),
            current_app=self.admin_site.name
        )

        msg_dict = {
            'email': request.user.email
        }

        msg = 'A test email was sent to {email}.'
        self.message_user(
            request,
            html.format_html(msg, **msg_dict),
            messages.SUCCESS
        )

        next_url = request.GET.get('next') or obj_url
        return HttpResponseRedirect(next_url)

    def schedule_view(self, request, object_id, extra_context=None):
        obj = self.get_object(request, admin.utils.unquote(object_id))
        opts = obj._meta
        app_label = opts.app_label
        preserved_filters = self.get_preserved_filters(request)
        form_url = admin.templatetags.admin_urls.add_preserved_filters(
            {
                'preserved_filters': preserved_filters,
                'opts': opts
            },
            ''
        )

        view_on_site_url = self.get_view_on_site_url(obj)
        request.current_app = self.admin_site.name

        if request.method == 'POST':
            obj.schedule()
            url = reverse(
                'admin:%s_%s_change' % (
                    opts.app_label,
                    opts.model_name
                ),
                args=(
                    admin.utils.quote(obj.pk),
                ),
                current_app=self.admin_site.name
            )

            msg = 'The message is scheduled for delivery.'
            self.message_user(request, msg, messages.SUCCESS)
            return HttpResponseRedirect(url)

        return TemplateResponse(
            request,
            'admin/newsletter/post/schedule_form.html',
            {
                'add': False,
                'change': False,
                'is_popup': (
                    '_popup' in request.POST or
                    '_popup' in request.GET
                ),
                'has_view_permission': self.has_view_permission(request, obj),
                'has_add_permission': self.has_add_permission(request),
                'has_change_permission': self.has_change_permission(
                    request,
                    obj
                ),
                'has_delete_permission': self.has_delete_permission(
                    request,
                    obj
                ),
                'has_absolute_url': view_on_site_url is not None,
                'absolute_url': view_on_site_url,
                'form_url': form_url,
                'object': obj,
                'opts': opts,
                'content_type_id': ContentType.objects.get_for_model(
                    obj,
                    for_concrete_model=False
                ).pk,
                'to_field_var': '_to_field',
                'is_popup_var': '_popup',
                'app_label': app_label,
                'title': 'Schedule delivery',
                **self.admin_site.each_context(request)
            }
        )

    def formfield_for_dbfield(self, field, request, **kwargs):
        if field.name in ('prompt', 'title'):
            kwargs['initial'] = Prompt.objects.exclude(
                pk__in=Post.objects.exclude(
                    prompt=None
                ).values_list(
                    'prompt_id',
                    flat=True
                ).distinct()
            ).first()
        elif field.name == 'episode':
            kwargs['initial'] = Episode.objects.exclude(
                pk__in=Post.objects.exclude(
                    episode=None
                ).values_list(
                    'episode_id',
                    flat=True
                ).distinct()
            ).first()

        elif field.name == 'published':
            kwargs['initial'] = timezone.now().date()

        return super().formfield_for_dbfield(field, request, **kwargs)

    class Media:
        css = {
            'screen': ('admin/css/newsletters.css',)
        }


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'last_seen')
    search_fields = (
        'email',
        'name'
    )

    def get_form(self, request, obj=None, change=False, **kwargs):
        if change:
            return super().get_form(request, obj, change, **kwargs)

        return ImportSubscribersForm

    def get_fields(self, request, obj):
        if obj:
            return (
                'email',
                'name',
                'subscribed',
                'last_seen',
                'timezone',
                ('city', 'country')
            )

        return (
            'emails',
        )

    def get_readonly_fields(self, request, obj):
        if obj:
            return (
                'subscribed',
                'last_seen',
                'city',
                'country'
            )

        return ()


@admin.register(Unsubscriber)
class UnsubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'unsubscribed')
    readonly_fields = ('email',)
    fields = ('email', 'unsubscribed')

    def has_add_permission(self, reuqest):
        return False
