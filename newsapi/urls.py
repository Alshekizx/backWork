#newsapi/urls.py

from django.contrib import admin
from django.urls import path, include
from news.view.custom_auth import CustomTokenLoginView
from news.views import CommentCreateView, NewsPostDetailView, NewsPostListView


urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/", include("news.urls")),
    path("api/comments/", CommentCreateView.as_view(), name="create-comment"),

    # Auth endpoints
    path("auth/token/login/", CustomTokenLoginView.as_view(), name="custom_token_login"),
    path('auth/', include('djoser.urls')),
]