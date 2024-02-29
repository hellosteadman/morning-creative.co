from django.urls import path
from .views import EpisodeListView, EpisodeDetailView


urlpatterns = (
    path('', EpisodeListView.as_view(), name='episode_list'),
    path('<int:number>/', EpisodeDetailView.as_view(), name='episode_detail')
)
