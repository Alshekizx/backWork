# newsapi/urls.py

from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static

def home(request):
    return HttpResponse("Hello, NaijaTalk API is running!")

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/", include("news.urls")),
    path('', home),
]

# ✅ Serve media files in development
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
