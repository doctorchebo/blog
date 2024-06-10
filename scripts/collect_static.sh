#!/bin/bash
source /home/ubuntu/blog/.venv/bin/activate
python /home/ubuntu/blog/manage.py collectstatic --noinput
