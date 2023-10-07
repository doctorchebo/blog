from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .models import ConfigurationCategory, ConfigurationOption, UserConfiguration
from blog_app.views import logout

@login_required
def configuration(request):
    user = request.user
    categories = ConfigurationCategory.objects.all()

    # Handle form submission when the user selects options
    category_id = request.POST.get('category_id')
    selected_option_ids = request.POST.getlist('selected_options')

    if category_id == None:
        default_category, created = ConfigurationCategory.objects.get_or_create(name="Mi Cuenta")
        category_id = default_category.id

    category = ConfigurationCategory.objects.get(pk=category_id)
    user_config, created = UserConfiguration.objects.get_or_create(
        user=user, category=category
    )
    if created:
        user_config.save()
    user_config.selected_options.clear()
    user_config.selected_options.add(*selected_option_ids)

    return render(
        request,
        'myconfigurations/configuration.html',
        {'categories': categories, 'user_config': user_config}
    )


@login_required
def delete_account(request):
    # Delete the user's account (you can customize this part)
    request.user.delete()

    # Log the user out
    logout(request)

    # Redirect to a confirmation page or homepage
    return redirect('blog_app:post_list')
