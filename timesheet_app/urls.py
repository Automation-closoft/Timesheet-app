from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from timesheet_app import views

urlpatterns = [
    path('', lambda request: redirect('login'), name='root'),
    path('admin/', admin.site.urls),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('home/', views.home, name='home'),
    path('logout/', views.logout_view, name='logout'),
    path('success/', views.success_view, name='success'),
    path('password_change/', views.password_change_view, name='password_change'),
    path('password_change_done/', views.password_change_done, name='password_change_done'),
    path('download-timesheets/', views.admin_download_timesheets, name='download_timesheets'),
]
