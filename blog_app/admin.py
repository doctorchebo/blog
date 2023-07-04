# blog_app/admin.py
from django.contrib import admin
from .models import Post, Comment, Tag, AboutSection

admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Tag)
admin.site.register(AboutSection)

# Register your models here.
