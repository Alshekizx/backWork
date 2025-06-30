from django.urls import path
from .views import NewsPostListView, NewsPostDetailView


urlpatterns = [
    path('news/', NewsPostListView.as_view(), name='news-list'),
    path('news/<uuid:id>/', NewsPostDetailView.as_view(), name='news-detail'),
]