# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import PageVisit
import json

@csrf_exempt  # You can use CSRF exemption for simplicity, but ensure security in production
def track_page_visit(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        # Extract data from the request
        url = data.get('url', '')
        visit_date = data.get('visit_date', '')
        duration = data.get('duration', 0)

        # Save the data in your database using the PageVisit model
        page_visit = PageVisit.objects.create(
            url=url,
            visit_date=visit_date,
            duration=duration,
            user=request.user

        )
        page_visit.save()

        return JsonResponse({'message': 'Page visit data saved successfully'})
