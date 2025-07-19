from django.urls import path
from .views import (
    AdvertisementCreateView,
    AdvertisementDetailView,
    AdvertisementListView,
    NewsPostListView,
    NewsPostDetailView,
    admin_stats,
    set_top_news,
    list_top_news,
    set_trending_news,
    list_trending_news,
    AdminSignupView,
    AdminLoginView,
    AdminListView,
    DeleteAdminView,
    track_blog_visit
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
    path('ads/<int:id>/', AdvertisementDetailView.as_view(), name='ad-detail'),

    # Admin (Manager + Employee) Management
    path('admin/signup/', AdminSignupView.as_view(), name='admin-signup'),
    path('admin/login/', AdminLoginView.as_view(), name='admin-login'),
    path('admin/list/', AdminListView.as_view(), name='admin-list'),
    path('admin/delete/<uuid:id>/', DeleteAdminView.as_view(), name='admin-delete'),
    
    path("admin/stats/", admin_stats),
    path('blogs/<uuid:post_id>/visit/', track_blog_visit),
]
