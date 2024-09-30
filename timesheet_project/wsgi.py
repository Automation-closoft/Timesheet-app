import os
import sys

# Optionally, add the project path to the system path (if necessary)
# sys.path.append('/opt/render/project/src')

# Set the default settings module for the 'django' program
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'timesheet_project.settings')

from django.core.wsgi import get_wsgi_application

# Create the WSGI application
application = get_wsgi_application()