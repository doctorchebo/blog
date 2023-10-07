from django.contrib import admin
from .models import ConfigurationCategory, ConfigurationOption, UserConfiguration

# Register the new configuration models
admin.site.register(ConfigurationCategory)
admin.site.register(ConfigurationOption)
admin.site.register(UserConfiguration)
