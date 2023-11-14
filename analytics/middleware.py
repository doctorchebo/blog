# analytics/middlewares.py
from django.utils import timezone
from .models import PageVisit

class PageVisitMiddleware:
    EXCLUDED_URLS = ['/admin/', '/is_subscribed/', '/message_url/', '/favicon.ico']  # Add URLs to exclude

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        self.process_request(request)
        return response

    def process_request(self, request):
        current_time = timezone.now()
        last_visit_time_str = request.session.get('last_visit_time')

        if last_visit_time_str:
            last_visit_time = timezone.datetime.strptime(last_visit_time_str, "%Y-%m-%d %H:%M:%S.%f%z")
            duration = current_time - last_visit_time

            # Check if the current URL is not in the excluded list
            if not any(request.path.startswith(prefix) for prefix in self.EXCLUDED_URLS):
                self.save_page_visit(request, duration)

        # Convert datetime object to string before storing in session
        request.session['last_visit_time'] = str(current_time)

    def save_page_visit(self, request, duration):
        url = request.path
        user = request.user if request.user.is_authenticated else None
        PageVisit.objects.create(url=url, user=user, duration=duration)
