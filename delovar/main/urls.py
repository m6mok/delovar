from django.urls import path

from . import views


app_name = 'main'


urlpatterns = [
    path('profile/', views.profile, name='profile'),
    path('about/', views.about, name='about'),
    path('prices/', views.prices, name='prices'),
    path('faq/', views.faq, name='faq'),
    path('', views.index, name='index')
]
