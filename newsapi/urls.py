#newsapi/urls.py

from django.contrib import admin
from django.urls import path, include
from news.view2.custom_auth import CustomTokenLoginView

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/", include("news.urls")),

]