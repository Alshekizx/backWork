from django.urls import path
from .views import NewsPostListView, NewsPostDetailView
from . import views

urlpatterns = [
    path('news/', NewsPostListView.as_view(), name='news-list'),
    path('news/<uuid:id>/', NewsPostDetailView.as_view(), name='news-detail'),
     path('top-news/set/', views.set_top_news),
    path('top-news/', views.list_top_news),
    
]