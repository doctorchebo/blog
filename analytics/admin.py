from django.contrib import admin
from .models import PageVisit

@admin.register(PageVisit)
class PageVisitAdmin(admin.ModelAdmin):
    list_display = ('url', 'visit_date', 'duration_in_seconds', 'user', 'ip_address')
    list_filter = ('url', 'visit_date', 'user', 'ip_address')

