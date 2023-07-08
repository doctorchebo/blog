#!/bin/bash
source /home/ubuntu/blog/my-django-blog/venv/bin/activate
python /home/ubuntu/blog/my-django-blog/manage.py collectstatic --noinput
