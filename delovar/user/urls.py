from django.urls import path
from django.contrib.auth.views import LogoutView

from . import views


app_name = 'user'


urlpatterns = [
    path('list/', views.user_list, name='list'),
    path('search/', views.user_search, name='search'),
    path('register/', views.register_user, name='register'),
    path('logout/', LogoutView.as_view(next_page='main:index'), name='logout'),
    path('edit/<str:pk>/', views.edit_user, name='edit'),
    path('password-reset/', views.password_reset, name='password_reset'),
]
