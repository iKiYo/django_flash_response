"""
import celery when Django project starts
"""
import celery
from .celery import app as celery_app
