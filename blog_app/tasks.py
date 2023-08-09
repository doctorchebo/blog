from django.core.mail import EmailMessage
from django_q.tasks import async_task
from django.template.loader import render_to_string
from .models import Subscriber
import os
from django.urls import reverse
import logging
from markdown import markdown

logger = logging.getLogger(__name__)

def send_newsletter(subject, body, img_path=None):
    domain = os.getenv('MY_WEBSITE_DOMAIN', 'http://127.0.0.1:8000')

    # Convert body from Markdown to HTML
    body = markdown(body)

    # Construct image_url with the obtained domain
    if img_path is not None:
        img_url = f'{domain}{img_path}'
        print(img_url)
    else:
        img_url = None
    subscribers = Subscriber.objects.all()
    for subscriber in subscribers:
        async_task(send_email, subject, body, [subscriber.email], img_url)

def send_email(subject, body, to, img_url):
    domain = os.getenv('MY_WEBSITE_DOMAIN', 'http://127.0.0.1:8000')

    unsubscribe_url = f'{domain}{reverse("blog_app:unsubscribe", args=[to[0]])}'

    email_content = render_to_string('emails/newsletter_email.html', {
        'title': subject,
        'body': body,
        'image_url': img_url,
        'unsubscribe_url': unsubscribe_url,
    })
    email = EmailMessage(subject, email_content, to=to)
    email.content_subtype = "html"  # This is needed to send HTML content
    email.send()