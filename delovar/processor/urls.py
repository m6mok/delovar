from django.urls import path

from . import views


app_name = 'processor'


urlpatterns = [
    path('case/search/', views.case_search, name='search'),
    path('case/<int:pk>/', views.CaseView.as_view(), name='case'),
    path(
        'case/all/',
        views.AllCasesListView.as_view(),
        name='cases'
    ),
    path('new/', views.CaseCreateView.as_view(), name='new'),
    path(
        'user/<int:pk/new/',
        views.AnotherUserCaseCreateView.as_view(),
        name='another_new_case'
    ),
    path('', views.CaseListView.as_view(), name='profile')
]
