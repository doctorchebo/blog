
# blog_app/urls.py
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'analytics'

urlpatterns = [
    path('track_page_visit/', views.track_page_visit, name='track_page_visit'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)