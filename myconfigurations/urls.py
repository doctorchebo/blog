from django.urls import path
from . import views

app_name = 'myconfigurations'

urlpatterns = [
    path('', views.configuration, name='configuration'),
    path('delete_account/', views.delete_account, name='delete_account'),
]
