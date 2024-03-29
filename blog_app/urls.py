# blog_app/urls.py
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'blog_app'

urlpatterns = [
    path('', views.PostListView.as_view(), name='post_list'),
    path('post/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('post/new/', views.PostCreateView.as_view(), name='post_new'),
    path('post/<int:pk>/edit/', views.PostUpdateView.as_view(), name='post_edit'),
    path('post/<int:pk>/delete/', views.PostDeleteView.as_view(), name='post_delete'),
    path('post/<int:pk>/comment/', views.add_comment_to_post, name='add_comment_to_post'),
    path('accounts/login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('ajax/add_reply_to_comment/', views.ajax_add_reply_to_comment, name='ajax_add_reply_to_comment'),
    path('about/', views.about, name='about'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('subscribe_page/', views.subscribe_page, name='subscribe_page'),
    path('newsletter/create/', views.create_newsletter, name='create_newsletter'),
    path('unsubscribe/<str:email>/', views.unsubscribe, name='unsubscribe'),
    path('unsubscribe_success/', views.unsubscribe_success, name='unsubscribe_success'),
    path('unsubscribe_fail/', views.unsubscribe_fail, name='unsubscribe_fail'),
    path('like_post/<int:post_id>/', views.like_post, name='like_post'),
    path('is_subscribed/', views.check_subscription_status, name='is_subscribed'),
    path('videos/', views.VideoListView.as_view(), name='videos'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)