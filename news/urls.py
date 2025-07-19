# file: backend/news/urls.py
from django.urls import path
from .views import (
    AdvertisementCreateView,
    AdvertisementDetailView,
    AdvertisementListView,
    NewsPostListView,
    NewsPostDetailView,
    set_top_news,
    list_top_news,
    set_trending_news,
    list_trending_news,
    CreateEmployeeView, 
    EmployeeListView, 
    DeleteEmployeeView,
    ManagerSignupView,
    ManagerLoginView,
    EmployeeLoginView
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
    
    # Manager + Employee Management
    path('manager/create-employee/', CreateEmployeeView.as_view(), name='create-employee'),
    path('manager/employees/', EmployeeListView.as_view(), name='list-employees'),
    path('manager/delete-employee/<uuid:id>/', DeleteEmployeeView.as_view(), name='delete-employee'),

    # Auth
    path('auth/manager/signup/', ManagerSignupView.as_view(), name='manager-signup'),
    path('auth/manager/login/', ManagerLoginView.as_view(), name='manager-login'),
    path('auth/employee/login/', EmployeeLoginView.as_view(), name='employee-login'),

]
