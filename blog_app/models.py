from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.urls import reverse

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True)

    def __str__(self):
        return self.title

    @property
    def reading_time(self):
        words_per_minute = 180 # The average reading speed is between 180 and 200 words per minute
        return int(len(self.content.split()) / words_per_minute)

    def get_absolute_url(self):
        return reverse('blog_app:post_detail', args=[self.id])

class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    root = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'Comment by {self.author} on {self.post}'
    def ordered_replies(self):
        return self.replies.order_by('-created_at')


class Tag(models.Model):
    name = models.CharField(max_length=30)
    posts = models.ManyToManyField(Post, related_name='tags')

    def __str__(self):
        return self.name

class AboutSection(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='about_images/')
    text_content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
      
class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
