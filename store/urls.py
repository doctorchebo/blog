from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.ProductListView.as_view(), name='product_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart_view'),
    path('checkout/', views.checkout, name='checkout'),
    path('remove-from-cart/', views.remove_from_cart, name='remove_from_cart'),
    path('my_purchases/', views.purchased_products, name='purchased_products'),
    path('get_content_objects/<int:content_type_id>/', views.get_content_objects, name='get_content_objects'),
    path('purchased_product/<int:product_id>/', views.purchased_product_detail, name='purchased_product_detail'),
    path('resources/', views.ResourcesListView.as_view(), name='resources'),
]
