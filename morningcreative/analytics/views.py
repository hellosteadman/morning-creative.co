from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import View
from .models import TrackedLink


class TrackedLinkView(View):
    def get(self, request, pk):
        obj = get_object_or_404(TrackedLink, pk=pk)

        if request.method == 'GET':
            click = obj.click(request)
            return HttpResponseRedirect(
                click.get_destination_url()
            )

        return HttpResponseRedirect(obj.url)
