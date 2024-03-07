# blog_app/views.py
import json
from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from .models import Post, Comment, AboutSection, Subscriber, Like, Category
from .forms import CommentForm, NewsletterForm, UnsubscribeForm, SignUpForm, LoginForm
from .tasks import send_newsletter
from store.models import VideoMedia
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.http import JsonResponse, HttpResponse  
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.decorators.http import require_http_methods
from django.utils import dateformat
from django.shortcuts import render
from store.views import merge_carts
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.urls import reverse
from myconfigurations.models import UserConfiguration, ConfigurationCategory
from markdown_deux import markdown
import requests
from django.conf import settings
import logging
from django.utils import timezone
import pytz
import re
from langdetect import detect
import os
import re

logger = logging.getLogger(__name__)

class TimeZoneMixin:
    def dispatch(self, request, *args, **kwargs):
        tzname = request.COOKIES.get('timezone')
        if tzname:
            timezone.activate(pytz.timezone(tzname))
        else:
            timezone.deactivate()
        return super().dispatch(request, *args, **kwargs)

class PostListView(TimeZoneMixin, ListView):
    model = Post
    template_name = 'blog_app/post_list.html'
    paginate_by = 5

    def get_queryset(self):
        queryset = Post.objects.prefetch_related('categories')

        # Get search parameters from the request
        search_query = self.request.GET.get('q', '')
        category_filter = self.request.GET.get('category', '')

        # Apply search filter based on title and category
        if search_query:
            queryset = queryset.filter(Q(title__icontains=search_query) | Q(categories__name__icontains=search_query))

        if category_filter:
            queryset = queryset.filter(categories__id=category_filter)

        # Use distinct() to eliminate duplicate results
        queryset = queryset.distinct()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Pass all categories to the template for the category dropdown
        context['all_categories'] = Category.objects.all().order_by('name')
        
        return context
class PostDetailView(TimeZoneMixin, DetailView):
    model = Post
    template_name = 'blog_app/post_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = Comment.objects.filter(post=self.object, parent=None).order_by('-created_at')  # Only top-level comments
        context['form'] = CommentForm()
        content_wordcount = len(self.object.content.split())
        context['reading_time'] = max(round(content_wordcount / 200), 1)
        
        # Remove markdown links
        plain_content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\1', self.object.content)
        
        # Remove markdown italics
        plain_content = re.sub(r'\*([^*]+)\*', r'\1', plain_content)
        plain_content = re.sub(r'_([^_]+)_', r'\1', plain_content)

        # Remove markdown bold
        plain_content = re.sub(r'\*\*([^*]+)\*\*', r'\1', plain_content)
        plain_content = re.sub(r'__([^_]+)__', r'\1', plain_content)

        # Remove markdown headers
        plain_content = re.sub(r'# ([^\n]+)', r'\1', plain_content)
        
        # Remove markdown lists
        plain_content = re.sub(r'\* ([^\n]+)', r'\1', plain_content)
        plain_content = re.sub(r'- ([^\n]+)', r'\1', plain_content)
        
        # Detect language of post content and add it to context
        context['language'] = detect(plain_content)
        
        # Store the plain content for future use
        context['plain_content'] = plain_content
        context['api_key'] = os.getenv('RESPONSIVE_VOICE_API_KEY')  # Adjust the variable name as needed

        return context

class PostCreateView(CreateView):
    model = Post
    template_name = 'blog_app/post_new.html'
    fields = ('title', 'content')

class PostUpdateView(UpdateView):
    model = Post
    template_name = 'blog_app/post_edit.html'
    fields = ('title', 'content')

class PostDeleteView(DeleteView):
    model = Post
    template_name = 'blog_app/post_delete.html'
    success_url = reverse_lazy('blog_app:post_list')

@login_required
def add_comment_to_post(request, pk, parent_comment_id=None):
    post = get_object_or_404(Post, pk=pk)
    parent_comment = None
    if parent_comment_id:
        parent_comment = get_object_or_404(Comment, pk=parent_comment_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.parent = parent_comment
            comment.save()
            # If the comment is a reply to another comment, its root is the same as the root of the parent comment.
            # If it's a top-level comment, its root is itself.
            comment.root = parent_comment.root if parent_comment else comment
            comment.save()

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':  # Check if AJAX request
                formatted_date = dateformat.format(comment.created_at, 'F j, Y, P')
                response = {
                    'status': 1,
                    'message': "Comment was posted successfully",
                    'comment_id': comment.id,
                    'content': comment.content,
                    'author': comment.author.username,
                    'date': formatted_date,
                }
                return JsonResponse(response)

            return redirect('blog_app:post_detail', pk=post.pk)
    else:
        form = CommentForm()
    return render(request, 'blog_app/post_detail.html', {'form': form})

def register(request):
    next_url = request.GET.get('next') # get the next URL from the GET request
    if request.method == "POST":
        # Validate that the username doesn't already exist
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            email = form.cleaned_data.get('email')
            
            # Check if the username already exists
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Este nombre de usuario ya existe. Por favor elige otro nombre de usuario')
            else:
                user = User.objects.create_user(username=username, password=password, email=email)
                user.save()
                
                # Save user configurations
                category, created = ConfigurationCategory.objects.get_or_create(name="Mi Cuenta")
                user_config = UserConfiguration(user=user, category=category)
                user_config.save()

                login(request, user)
                # Merge session cart with user cart after user logs in
                merge_carts(request)
                
                next_url = request.POST.get('next') # get the next URL from the POST request
                if next_url: # if next URL exists, redirect there
                    return redirect(next_url)
                return redirect('blog_app:post_list')
    else:
        form = SignUpForm()
    return render(request, 'blog_app/signup.html', {'form': form, 'next': next_url})

def login_view(request):
    next_url = request.GET.get('next') # get the next URL from the GET request
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # Merge session cart with user cart after user logs in
                merge_carts(request)
                
                next_url = request.POST.get('next') # get the next URL from the POST request
                print(f'next_url = "{next_url}"')
                if next_url: # if next URL exists, redirect there
                    return redirect(next_url)
                return redirect('blog_app:post_list')
            else:
                messages.error(request, 'Usuario o password inválido.')
    else:
        form = LoginForm()

    return render(request, 'blog_app/login.html', {'form': form, 'next': next_url})


def logout_view(request):
    logout(request)
    return redirect('blog_app:post_list')

@login_required
@require_POST
def ajax_add_reply_to_comment(request):
    form = CommentForm(data=request.POST)
    if form.is_valid():
        reply = form.save(commit=False)
        reply.author = request.user
        parent_comment_id = request.POST.get('parent_comment')
        if parent_comment_id:
            parent_comment = get_object_or_404(Comment, pk=parent_comment_id)
            reply.parent= parent_comment
            reply.post = parent_comment.post
            # Update root_id based on parent comment
            if parent_comment.root is None:  # This means parent comment is a root comment
                reply.root = None  # set root to None for replies to root comments
            else:  # This means parent comment is a reply itself
                reply.root = parent_comment.root
        reply.save()
        formatted_date = dateformat.format(reply.created_at, 'F j, Y, P')
        response = {
            'status': 1,
            'message': "Reply was posted successfully",
            'reply_id': reply.id,
            'content': reply.content,
            'author': reply.author.username,
            'date': formatted_date,
        }
        return JsonResponse(response)
    else:
        return JsonResponse({'status': 0, 'message': "Invalid form"})
    
def about(request):
    try:
        video_intro = VideoMedia.objects.get(name="Intro")
    except VideoMedia.DoesNotExist:
        video_intro = None
    sections = AboutSection.objects.exclude(title="Intro").order_by('created_at')
    intro = AboutSection.objects.get(title="Intro")
    # Convert markdown to HTML for each section
    for section in sections:
        section.text_content = markdown(section.text_content)

    intro.text_content = markdown(intro.text_content)
    AWS_S3_CUSTOM_DOMAIN = os.getenv('AWS_S3_CUSTOM_DOMAIN')
    cloudfront_domain = f'https://{AWS_S3_CUSTOM_DOMAIN}'

    context = {
        'sections': sections,
        'intro' : intro,
        'video_intro': video_intro,
        'cloudfront_domain': cloudfront_domain
    }
    return render(request, 'blog_app/about.html', context)

@csrf_exempt
def subscribe(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        if email:
            subscriber, created = Subscriber.objects.get_or_create(email=email)
            if created:
                domain = os.getenv('MY_WEBSITE_DOMAIN', 'http://127.0.0.1:8000')
                unsubscribe_url = f'{domain}{reverse("blog_app:unsubscribe", kwargs={"email": email})}'
                document_url = f'https://{os.getenv('AWS_S3_CUSTOM_DOMAIN')}.s3.amazonaws.com/free_document.pdf'
                # Send the welcome email
                subject = '¡Bienvenido a nuestro boletín!'
                message = strip_tags(render_to_string('emails/welcome_email.html', {'user': subscriber.user, 'document_url': document_url}))
                from_email = os.getenv('DEFAULT_FROM_EMAIL')  # Replace with your email address
                recipient_list = [email]  # Email address of the subscriber
                
                send_mail(subject, message, from_email, recipient_list, html_message=render_to_string('emails/welcome_email.html', {'user': subscriber.user, 'document_url': document_url, 'unsubscribe_url': unsubscribe_url}))

                return JsonResponse({'status': 'ok', 'message': 'Gracias por suscribirte!'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Este email ya está suscrito!'}, status=400)
        else:
            return JsonResponse({'status': 'error', 'message': 'Email inválido.'}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request.'}, status=405)

@login_required
def check_subscription_status(request):
    is_subscribed = Subscriber.objects.filter(user=request.user).exists()
    return JsonResponse({'is_subscribed': is_subscribed})

def subscribe_page(request):
    return render(request, 'blog_app/subscribe_page.html')

def admin_check(user):
    return user.is_superuser

@login_required
@user_passes_test(admin_check)
def create_newsletter(request):
    if request.method == 'POST':
        form = NewsletterForm(request.POST, request.FILES)
        if form.is_valid():
            newsletter = form.save()  # Save newsletter as it is without converting to HTML
            # Get the path of the image
            img_path = None
            if newsletter.image:
                img_path = newsletter.image.url  # use .url instead of .path
            send_newsletter(newsletter.subject, newsletter.body, img_path)  # Pass additional arguments
            messages.success(request, 'El newsletter fue enviado con éxito!')
            return redirect('blog_app:create_newsletter')
        else:
            print(form.errors)
            messages.error(request, 'There was an error with your form. Please check and try again.')
    else:
        form = NewsletterForm()

    return render(request, 'blog_app/create_newsletter.html', {'form': form})

def unsubscribe(request, email):
    if request.method == "POST":
        Subscriber.objects.filter(email=email).delete()
        return redirect('blog_app:unsubscribe_success')
    else:
        if not Subscriber.objects.filter(email=email).exists():
            return redirect('blog_app:unsubscribe_fail')
    return render(request, 'blog_app/unsubscribe.html', {'email': email})

def unsubscribe_success(request):
    return render(request, 'blog_app/unsubscribe_success.html')

def unsubscribe_fail(request):
    return render(request, 'blog_app/unsubscribe_fail.html')

def like_post(request, post_id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not authenticated"}, status=401)

    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)

    if not created:
        like.delete()
        return JsonResponse({"likes_count": post.likes_count(), "liked": False})

    return JsonResponse({"likes_count": post.likes_count(), "liked": True})


class VideoListView(ListView):
    model = VideoMedia
    template_name = 'blog_app/videos.html'
    paginate_by = 5

    def get_queryset(self):
        queryset = VideoMedia.objects.exclude(name="Intro")
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        AWS_S3_CUSTOM_DOMAIN = os.getenv('AWS_S3_CUSTOM_DOMAIN')
        context["cloudfront_domain"] = f'https://{AWS_S3_CUSTOM_DOMAIN}'
        context["videos"] = self.get_queryset()  # Reuse the queryset
        return context
