from django.urls import path
from morningcreative.prompts.views import LatestPromptView


urlpatterns = (
    path('', LatestPromptView.as_view(), name='latest_prompt'),
)
