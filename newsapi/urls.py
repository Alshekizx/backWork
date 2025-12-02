#newsapi/urls.py

from django.contrib import admin
from django.urls import path, include
from news.view2.custom_auth import CustomTokenLoginView
from django.http import HttpResponse

def home(request):
    return HttpResponse("Hello, NaijaTalk API is running!")

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/", include("news.urls")),

]