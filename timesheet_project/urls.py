from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('login')),  # Redirect the root URL to the login page
    path('', include('timesheet_app.urls')),  # Include the app's URLs
]
