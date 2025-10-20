#file: news/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from view.custom_auth import CustomTokenLoginView

from .views import (
    AdvertisementCreateView, AdvertisementDetailView, AdvertisementListView, CommentCreateView,
    ContactUsDeleteView, ContactUsListCreateView,
    CreateEmployeeView, DeleteEmployeeView, EmployeeListView,
    NewsCategoryViewSet, NewsPostListView, NewsPostDetailView,
    NewsSourceViewSet, NewsletterHistoryListView, SendNewsletterView,
    ToggleContactSeenStatus, check_email_availability, check_username_availability,
    set_top_news, list_top_news, set_trending_news, list_trending_news,
    AdminSignupView, AdminLoginView, AdminListView, DeleteAdminView,
    track_blog_visit, admin_dashboard_stats, fetch_news_view,
    NewsLetterSubscriptionView, track_category_visit, UserListView, 
    delete_user, reset_user_password, google_login
)

router = DefaultRouter()
router.register(r'categories', NewsCategoryViewSet, basename='categories')
router.register(r'sources', NewsSourceViewSet, basename='sources')

urlpatterns = [
       # ✅ Router endpoints (categories, sources)
    path('news/', NewsPostListView.as_view(), name='news-list'),
    path('news/<uuid:id>/', NewsPostDetailView.as_view(), name='news-detail'),
    path('top-news/set/', set_top_news),
    path('top-news/', list_top_news),
    path('trending-news/set/', set_trending_news),
    path('trending-news/', list_trending_news),

    path('ads/', AdvertisementListView.as_view(), name='ads-list'),
    path('ads/create/', AdvertisementCreateView.as_view(), name='ads-create'),
    path('ads/<uuid:id>/', AdvertisementDetailView.as_view(), name='ad-detail'),

    # Admin Management
    path('admin/signup/', AdminSignupView.as_view(), name='admin-signup'),
    path('admin/login/', AdminLoginView.as_view(), name='admin-login'),
    path('admin/list/', AdminListView.as_view(), name='admin-list'),
    path('admin/delete/<uuid:id>/', DeleteAdminView.as_view(), name='admin-delete'),
    path("comments/", CommentCreateView.as_view(), name="create-comment"),

    path('blogs/<uuid:post_id>/visit/', track_blog_visit),
    path("admin/stats/", admin_dashboard_stats, name="dashboard-stats"),

    path('fetch-news/', fetch_news_view, name='fetch-news'),

    path('employees/', EmployeeListView.as_view(), name='employee-list'),
    path('employees/create/', CreateEmployeeView.as_view(), name='employee-create'),
    path('employees/delete/<uuid:id>/', DeleteEmployeeView.as_view(), name='employee-delete'),

    path("auth/check-username/", check_username_availability),
    path("auth/check-email/", check_email_availability),
    path("auth/token/login/", CustomTokenLoginView.as_view(), name="custom_token_login"),
    path("auth/google-login/", google_login, name="google_login"),
    path("auth/", include("djoser.urls")),

    path('subscribe-newsletter/', NewsLetterSubscriptionView.as_view(), name='subscribe-newsletter'),
    path('newsletter/send/', SendNewsletterView.as_view(), name='send-newsletter'),
    path('newsletter/history/', NewsletterHistoryListView.as_view(), name='newsletter-history'),

    path('contact/', ContactUsListCreateView.as_view(), name='contact-list-create'),
    path('contact/<int:pk>/', ContactUsDeleteView.as_view(), name='contact-delete'),
    path('contact/<int:pk>/toggle-seen/', ToggleContactSeenStatus.as_view(), name='toggle-contact-seen'),
    path("track-category/", track_category_visit, name="track-category"),

    path("users/", UserListView.as_view(), name="user-list"),
    path("users/<uuid:id>/delete/", delete_user, name="delete-user"),
    path("users/<uuid:id>/reset-password/", reset_user_password, name="reset-password"),


    path("", include(router.urls)),
]
