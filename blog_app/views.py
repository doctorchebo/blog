# blog_app/views.py
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from .models import Post, Comment, AboutSection, Subscriber
from .forms import CommentForm, NewsletterForm, UnsubscribeForm
from .tasks import send_newsletter
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import SignUpForm, LoginForm
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.decorators.http import require_http_methods
from django.utils import dateformat
from django.shortcuts import render
from markdown_deux import markdown
import requests
import logging

logger = logging.getLogger(__name__)

class PostListView(ListView):
    model = Post
    template_name = 'blog_app/post_list.html'
    paginate_by = 5
    ordering = ['-date_posted']
class PostDetailView(DetailView):
    model = Post
    template_name = 'blog_app/post_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)    
        context['comments'] = Comment.objects.filter(post=self.object, parent=None).order_by('-created_at')  # Only top-level comments
        context['form'] = CommentForm()
        content_wordcount = len(self.object.content.split())
        context['reading_time'] = max(round(content_wordcount / 200), 1)
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
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            email = form.cleaned_data.get('email')
            user = User.objects.create_user(username=username, password=password, email=email)
            user.save() 
            login(request, user)
            next_url = request.POST.get('next') # get the next URL from the POST request
            if next_url: # if next URL exists, redirect there
                return redirect(next_url)
            return redirect('blog_app:post_list')
        # Don't create a new form here, as it would discard the errors
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
    sections = AboutSection.objects.exclude(title="Intro").order_by('created_at')
    intro = AboutSection.objects.get(title="Intro")
    # Convert markdown to HTML for each section
    for section in sections:
        section.text_content = markdown(section.text_content)

    intro.text_content = markdown(intro.text_content)

    context = {
        'sections': sections,
        'intro' : intro
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
                return JsonResponse({'status': 'ok', 'message': 'Gracias por suscribirte!'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Este email ya está suscrito!'}, status=400)
        else:
            return JsonResponse({'status': 'error', 'message': 'Email inválido.'}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request.'}, status=405)

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

@csrf_exempt
@require_POST
def sns_notification(request):
    try:
        # AWS sends JSON with text/plain mimetype
        message = json.loads(request.body)
        logger.info(f'Received message: {message}')  # Log the received message

        if message.get('Type') == 'Notification':
            notification = json.loads(message.get('Message', '{}'))
            notification_type = notification.get('notificationType')

            if notification_type == 'Bounce':
                bounce = notification.get('bounce')
                if bounce:
                    bouncedRecipients = bounce.get('bouncedRecipients', [])
                    if bouncedRecipients:
                        email = bouncedRecipients[0].get('emailAddress')
                        if email:
                            # Unsubscribe this email address
                            Subscriber.objects.filter(email=email).delete()
                            logger.info(f'Bounce Notification received for email: {email}. Unsubscribed the email.')  # Log the email that was unsubscribed

            elif notification_type == 'Complaint':
                complaint = notification.get('complaint')
                if complaint:
                    complainedRecipients = complaint.get('complainedRecipients', [])
                    if complainedRecipients:
                        email = complainedRecipients[0].get('emailAddress')
                        if email:
                            # Unsubscribe this email address
                            Subscriber.objects.filter(email=email).delete()
                            logger.info(f'Complaint Notification received for email: {email}. Unsubscribed the email.')  # Log the email that was unsubscribed

            elif notification_type:
                logger.warning(f'Unhandled notification type received: {notification_type}')  # Log unhandled notification types as warnings
            else:
                logger.warning('Invalid notification message received.')  # Log invalid notification messages as warnings
        else:
            logger.warning('Message type is not a notification.')  # Log messages that are not notifications as warnings

        return HttpResponse(status=200)

    except Exception as e:
        logger.error(f'An error occurred while processing SNS message: {str(e)}')  # Log the error
        return HttpResponse(status=500)


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
