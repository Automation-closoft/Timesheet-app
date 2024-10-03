from django.urls import path
from .views import (
    signup,
    login_view,
    home,
    logout_view,
    success_view,
    password_change_view,
    password_change_done,
    admin_download_timesheets,  # Import the new view
)

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('login/', login_view, name='login'),
    path('home/', home, name='home'),
    path('logout/', logout_view, name='logout'),
    path('success/', success_view, name='success'),
    path('password_change/', password_change_view, name='password_change'),
    path('password_change_done/', password_change_done, name='password_change_done'),
    path('admin/download-timesheets/', admin_download_timesheets, name='admin_download_timesheets'),  # New URL for downloading timesheets
]
