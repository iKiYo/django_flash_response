import os
from celery import Celery

# Set enviroment varibale for celery command
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sla_app_project.settings')
# Create an instance of Celery application
app = Celery('sla_app_project')
# Set a prefix of CELERY_ as a namespace rule in the app
app.config_from_object('django.conf:settings', namespace='CELERY')
# Set to search async tasks automatically
app.autodiscover_tasks()

