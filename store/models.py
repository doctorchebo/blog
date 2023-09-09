from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from polymorphic.models import PolymorphicModel

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/')
    discount_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.0, validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ]
    )
    is_digital = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
    @property
    def discounted_price(self):
        return self.price * (1 - self.discount_percentage / 100)

class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.total_price = self.product.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order of {self.product.name} by {self.user.username}"
    
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'product')

    def total(self):
        return self.product.price * self.quantity

class BillingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=12)
    country = models.CharField(max_length=100)
    
    def __str__(self):
        return f'{self.user.username} - {self.street_address}'

class UserPurchases(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    purchase_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.product}'

class MediaContent(PolymorphicModel):
    name = models.CharField(max_length=200)
    description = models.TextField()

    class Meta:
        verbose_name = "Media Content" # Default, won't be used

class ImageMedia(MediaContent):
    file = models.ImageField(upload_to='media/images/')

    class Meta:
        verbose_name = "Imágenes"

    def __str__(self):
        return self.name or str(self.id)

class VideoMedia(MediaContent):
    video_url = models.URLField()

    class Meta:
        verbose_name = "Videos"

    def __str__(self):
        return self.name or str(self.id)

class DocumentMedia(MediaContent):
    file = models.FileField(upload_to='media/documents/')

    class Meta:
        verbose_name = "Documentos"
    
    def __str__(self):
        return self.name or str(self.id)

class Lesson(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)  # To determine the order of lessons within a product

    class Meta:
        ordering = ['order', 'id']  # default ordering

    def __str__(self):
        return self.title

# This model links media with products
class ProductMedia(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, null=True, blank=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    order = models.PositiveIntegerField(default=0)  # To determine the order of media within a lesson

    class Meta:
        ordering = ['order', 'id']  # default ordering

