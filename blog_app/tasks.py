from django.core.mail import EmailMessage
from django_q.tasks import async_task
from .models import Subscriber

import logging

logger = logging.getLogger(__name__)

def send_newsletter(subject, body, img_path=None):
    subscribers = Subscriber.objects.all()
    for subscriber in subscribers:
        async_task(send_email, subject, body, [subscriber.email], img_path)

def send_email(subject, body, to, img_path):
    email = EmailMessage(subject, body, to=to)
    if img_path is not None:
        email.attach_file(img_path)
    email.send()
