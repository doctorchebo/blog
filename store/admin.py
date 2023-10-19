from django.contrib import admin
from .models import Product, Order, UserPurchases, Lesson, ProductMedia, ImageMedia, VideoMedia, DocumentMedia, Resource, MediaContent
from .forms import ProductMediaInlineForm
from django.contrib import admin
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin, PolymorphicChildModelFilter
from django.contrib.contenttypes.models import ContentType

# Register your models here.
admin.site.register(Order)
admin.site.register(UserPurchases)

@admin.register(MediaContent)
class MediaContentAdmin(PolymorphicParentModelAdmin):
    base_model = MediaContent
    child_models = (ImageMedia, VideoMedia, DocumentMedia)
    list_filter = (PolymorphicChildModelFilter,)

@admin.register(ImageMedia)
class ImageMediaAdmin(PolymorphicChildModelAdmin):
    base_model = ImageMedia
    list_display = ('name', 'description', 'file')

@admin.register(VideoMedia)
class VideoMediaAdmin(PolymorphicChildModelAdmin):
    base_model = VideoMedia
    list_display = ('name', 'description', 'video_url', 'video_file')

@admin.register(DocumentMedia)
class DocumentMediaAdmin(PolymorphicChildModelAdmin):
    base_model = DocumentMedia
    list_display = ('name', 'description', 'file')

class ProductMediaInline(admin.TabularInline):
    model = ProductMedia
    form = ProductMediaInlineForm
    extra = 1

    class Media:
        js = ('admin/js/admin.js',)

    def get_formset(self, request, obj=None, **kwargs):
        request._obj_ = obj
        return super(ProductMediaInline, self).get_formset(request, obj, **kwargs)

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ['title', 'description', 'order']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [LessonInline, ProductMediaInline]

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'product')
    list_filter = ('product',)
    search_fields = ['title']

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'resource_type', 'date_added']
    list_filter = ['resource_type']
    search_fields = ['title', 'description']


