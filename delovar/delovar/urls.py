from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('z/', include('processor.urls', 'processor')),
    path('auth/', include('user.urls', 'user')),
    path('', include('main.urls', 'main'))
]
