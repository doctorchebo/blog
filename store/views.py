from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Order, Cart, CartItem, UserPurchases, ProductMedia
from .forms import BillingAddressForm
from django.contrib.auth.signals import user_logged_out
from django.db.models import Sum
from django.shortcuts import render, redirect
from django.conf import settings
from django.views.generic import ListView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render, get_object_or_404
from copy import copy
import paypalrestsdk
from dotenv import load_dotenv
import os
import json


class ProductListView(ListView):
    model = Product
    template_name = 'store/product_list.html'
    context_object_name = 'products'
    paginate_by = 4

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = get_or_create_cart(self.request)
        cart_count = CartItem.objects.filter(cart=cart).aggregate(total=Sum('quantity'))['total'] or 0
        context['cart_count'] = cart_count
        return context


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'store/product_detail.html', {'product': product})

@csrf_exempt
def add_to_cart(request):
    data = json.loads(request.body)
    product_id_str = data.get('product_id')
    quantity_str = data.get('quantity')

    cart = get_or_create_cart(request)
    product = get_object_or_404(Product, id=product_id_str)

    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if created:
        # Set the initial quantity for the newly created CartItem
        cart_item.quantity = int(quantity_str)
        cart_item.save()
    else:
        # If CartItem already exists, increase the quantity
        cart_item.quantity += int(quantity_str)  # Ensure you convert the string to int before addition
        cart_item.save()

    # Get the new cart count
    new_cart_count = sum(item.quantity for item in cart.cartitem_set.all())

    return JsonResponse({"message": "Producto añadido al carrito!", "success": True, "cart_count": new_cart_count})


def get_or_create_cart(request):
    if request.user.is_authenticated:
        # If the user is authenticated, get or create the cart for the user
        cart, created = Cart.objects.get_or_create(user=request.user, is_ordered=False)
    else:
        # If user is not authenticated, get or create the cart using session id
        cart_id = request.session.get('cart_id')
        if cart_id:
            try:
                cart = Cart.objects.get(id=cart_id)
            except Cart.DoesNotExist:
                cart = Cart.objects.create()
                request.session['cart_id'] = cart.id
        else:
            cart = Cart.objects.create()
            request.session['cart_id'] = cart.id
    return cart

def remove_from_cart(request, product_id):
    cart = get_or_create_cart(request)
    product = get_object_or_404(Product, id=product_id)
    CartItem.objects.filter(cart=cart, product=product).delete()
    
    return redirect('store:cart_view')

def delete_cart(sender, request, **kwargs):
    if 'cart_id' in request.session:
        try:
            cart = Cart.objects.get(id=request.session['cart_id'])
            cart.delete()
            del request.session['cart_id']
        except Cart.DoesNotExist:
            pass

user_logged_out.connect(delete_cart)

def cart_view(request):
    cart = get_or_create_cart(request)
    
    # Fetch CartItems for this cart from the database.
    cart_items_db = CartItem.objects.filter(cart=cart)

    cart_items = []
    total_price = 0

    for item in cart_items_db:
        product = item.product
        quantity = item.quantity
        total_price += product.price * quantity

        cart_items.append({
            'product': product,
            'quantity': quantity,
            'total': product.price * quantity
        })

    return render(request, 'store/cart_view.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })

def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        cart_id = request.session.get('cart_id')
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
        else:
            cart = Cart.objects.create()
            request.session['cart_id'] = cart.id
    return cart

@csrf_exempt
def remove_from_cart(request):
    data = json.loads(request.body)
    product_id = data.get('product_id')
    
    cart = get_or_create_cart(request)
    product = get_object_or_404(Product, id=product_id)

    cart_item = CartItem.objects.filter(cart=cart, product=product).first()
    if cart_item:
        cart_item.delete()

    # Recalculate the total price after removal
    total_price = sum(item.product.price * item.quantity for item in cart.cartitem_set.all())

    return JsonResponse({"message": "Producto eliminado del carrito!", "success": True, "total_price": total_price})

def checkout(request):
    return render(request, 'store/checkout.html')

def payment_successful(request):
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')
    
    payment = paypalrestsdk.Payment.find(payment_id)
    if payment.execute({"payer_id": payer_id}):
        # Payment was successful. Save the details, finalize order, etc.
        return render(request, 'store/success.html')
    else:
        return render(request, 'store/error.html', {'error': payment.error})

def purchased_products(request):
    user = request.user

    # Ensure the user is logged in
    if not user.is_authenticated:
        return redirect('blog_app:login')

    purchases = UserPurchases.objects.filter(user=user, product__is_digital=True)  # Added product__is_digital=True

    # Extract the products from the purchase objects
    purchased_products = [purchase.product for purchase in purchases]

    return render(request, 'store/purchased_products.html', {
        'products': purchased_products
    })

@login_required
def merge_carts(request):
    session_cart_id = request.session.get('cart_id')
    if session_cart_id:
        try:
            session_cart = Cart.objects.get(id=session_cart_id)
            user_cart, created = Cart.objects.get_or_create(user=request.user)
            
            # Merge cart items from session_cart into user_cart
            for session_cart_item in session_cart.cartitem_set.all():
                cart_item, created = CartItem.objects.get_or_create(cart=user_cart, product=session_cart_item.product)
                if created:
                    cart_item.quantity = session_cart_item.quantity
                else:
                    cart_item.quantity += session_cart_item.quantity
                cart_item.save()

            # Remove the old session cart
            session_cart.delete()
            if 'cart_id' in request.session:
                del request.session['cart_id']
        except Cart.DoesNotExist:
            pass

    return redirect('store:cart_view')  # Redirect to the cart view or any other view

def get_content_objects(request, content_type_id):
    content_type = ContentType.objects.get(id=content_type_id)
    model = content_type.model_class()
    objects = model.objects.all()
    data = {obj.id: str(obj) for obj in objects}
    return JsonResponse(data)

def purchased_product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    media_contents = ProductMedia.objects.filter(product=product)

    # Loop through media_contents and add the verbose_name to each object
    for media_content in media_contents:
        media_content.verbose_name = media_content.content_type.model_class()._meta.verbose_name

    context = {
        'product': product,
        'media_contents': media_contents,
    }
    return render(request, 'store/purchased_product_detail.html', context)

def purchased_product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    media_contents = ProductMedia.objects.filter(product=product).prefetch_related('content_object')

    unique_content_types = []
    for content in media_contents:
        if content.content_type not in unique_content_types:
            content_type_clone = copy(content.content_type)
            content_type_clone.verbose_name = content_type_clone.model_class()._meta.verbose_name
            unique_content_types.append(content_type_clone)

    context = {
        'product': product,
        'media_contents': media_contents,
        'unique_content_types': unique_content_types
    }
    return render(request, 'store/purchased_product_detail.html', context)


