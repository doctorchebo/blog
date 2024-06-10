#!/bin/bash
source /home/ubuntu/blog/.venv/bin/activate
python3 /home/ubuntu/blog/manage.py collectstatic --noinput
