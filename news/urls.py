# file: backend/news/urls.py
from django.urls import path
from .views import (
    AdvertisementCreateView,
    AdvertisementListView,
    NewsPostListView,
    NewsPostDetailView,
    set_top_news,
    list_top_news,
    set_trending_news,
    list_trending_news,
)

urlpatterns = [
    path('news/', NewsPostListView.as_view(), name='news-list'),
    path('news/<uuid:id>/', NewsPostDetailView.as_view(), name='news-detail'),
    path('top-news/set/', set_top_news),
    path('top-news/', list_top_news),

    path('trending-news/set/', set_trending_news),
    path('trending-news/', list_trending_news),
    
    path('ads/', AdvertisementListView.as_view(), name='ads-list'),
    path('ads/create/', AdvertisementCreateView.as_view(), name='ads-create'),
]
