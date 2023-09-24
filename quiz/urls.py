from django.urls import path
from . import views

app_name = 'quiz'

urlpatterns = [
    path('', views.questionnaire, name='questionnaire'),
    path('submit_answers/', views.submit_answers, name='submit_answers'),
    path('result/', views.result, name='result'),
    path('show_answers/', views.show_answers, name='show_answers'),
]