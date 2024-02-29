from django.urls import path
from .views import TrackedLinkView


urlpatterns = (
    path('t/<pk>/', TrackedLinkView.as_view(), name='tracked_link_redirect'),
)
