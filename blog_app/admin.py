# blog_app/admin.py
from django.contrib import admin
from .models import Post, Comment, Tag, AboutSection, Category

admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Tag)
admin.site.register(AboutSection)
admin.site.register(Category)

# Register your models here.
