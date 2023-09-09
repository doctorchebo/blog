from django import forms
from .models import BillingAddress, ProductMedia, MediaContent, ImageMedia, VideoMedia, DocumentMedia 
from django.contrib.contenttypes.models import ContentType
from django import forms
from django.core.exceptions import ValidationError

class BillingAddressForm(forms.ModelForm):
    class Meta:
        model = BillingAddress
        fields = ['street_address', 'city', 'state', 'zip_code', 'country']

class ProductMediaInlineForm(forms.ModelForm):
    class Meta:
        model = ProductMedia
        fields = "__all__"
    
    # Define your choices outside so they are computed once and not on every form instantiation
    related_models = [ImageMedia, VideoMedia, DocumentMedia]
    object_names_and_ids = []


