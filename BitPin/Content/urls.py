from django.urls import path
from Content.views import ContentView, ScoreView

app_name = 'content'

urlpatterns = [
    path('', ContentView.as_view(), name='list'),
    path('score/', ScoreView.as_view(), name='score'),
]