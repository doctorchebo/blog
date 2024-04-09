from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class PageVisit(models.Model):
    url = models.CharField(max_length=255)
    visit_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    duration = models.DurationField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def duration_in_seconds(self):
        # Calculate the duration in seconds, rounded to two decimal places
        if self.duration:
            return round(self.duration.total_seconds(), 2)
        return 0.00  # You can change the default value as needed
    duration_in_seconds.short_description = 'Duration (seconds)'  # Admin display name
