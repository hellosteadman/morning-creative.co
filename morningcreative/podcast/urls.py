from django.urls import path
from .views import EpisodeListView, EpisodeDetailView, ListenView


urlpatterns = (
    path('episodes/', EpisodeListView.as_view(), name='episode_list'),
    path('<int:number>/', EpisodeDetailView.as_view(), name='episode_detail'),
    path('listen/', ListenView.as_view(), name='listen')
)
