from django.urls import path

from . import views


app_name = 'main'


urlpatterns = [
    path('about/', views.about, name='about'),
    path('prices/', views.prices, name='prices'),
    path('faq/', views.faq, name='faq'),
    path('profile/', views.profile, name='profile'),
    path('cases/new/', views.new_case, name='new_case'),
    path('cases/case/<str:pk>/', views.case_detail, name='case'),
    path('cases/case/<str:pk>/delete/', views.delete_case, name='delete_case'),
    path('cases/case/<str:pk>/check_receipt/', views.check_receipt, name='check_receipt'),
    path('cases/case/<str:pk>/check_statement/', views.check_statement, name='check_statement'),
    path('cases/case/<str:pk>/check_upload/', views.check_upload, name='check_upload'),
    path('cases/case/<str:pk>/document_pack/', views.create_document_pack, name='create_document_pack'),
    path('', views.IndexView.as_view(), name='index')
]
