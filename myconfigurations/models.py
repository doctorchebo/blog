from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

# Configuration models
class ConfigurationCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class ConfigurationOption(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=50)
    options = models.JSONField(default=dict)
    category = models.ForeignKey(ConfigurationCategory, on_delete=models.CASCADE, related_name='options')

    def __str__(self):
        return self.name

class UserConfiguration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(ConfigurationCategory, on_delete=models.CASCADE)
    selected_options = models.ManyToManyField(ConfigurationOption, related_name='user_configurations')

    def __str__(self):
        return f'{self.user.username} - {self.category.name}'