import io
import logging
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.utils import timezone
from .models import UserProfile, TimesheetEntry
from .forms import UserRegistrationForm
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
import openpyxl
from django.http import HttpResponse

logger = logging.getLogger(__name__)

def format_hours_and_minutes(total_hours):
    hours = int(total_hours)
    minutes = int((total_hours - hours) * 60)
    return f"{hours}h {minutes}m"


@login_required
def signup(request):
    if not request.user.is_staff:
        raise PermissionDenied("You do not have permission to create new users.")

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            employee_name = form.cleaned_data.get('employee_name')

            user = User.objects.create_user(username=username, password=password)
            UserProfile.objects.create(user=user, employee_name=employee_name)

            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')


@login_required
def home(request):
    current_date = timezone.now().date()

    if request.method == 'POST':
        project = request.POST.get('project')
        date = request.POST.get('date')
        login_time = request.POST.get('login_time')
        logout_time = request.POST.get('logout_time')

        if not all([project, date, login_time, logout_time]):
            messages.error(request, "Please fill in all fields.")
            return render(request, 'home.html', {'current_date': current_date})

        try:
            login_time_obj = datetime.strptime(login_time, '%H:%M')
            logout_time_obj = datetime.strptime(logout_time, '%H:%M')
            date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Please enter correct date and time format.")
            return render(request, 'home.html', {'current_date': current_date})

        hours_worked = (logout_time_obj - login_time_obj).seconds / 3600
        formatted_hours_worked = format_hours_and_minutes(hours_worked)

        # ✅ SAVE DIRECTLY TO NEON DATABASE INSTANTLY
        TimesheetEntry.objects.update_or_create(
            user=request.user,
            date=date_obj,
            defaults={
                'project': project,
                'login_time': login_time,
                'logout_time': logout_time,
                'hours_worked': formatted_hours_worked
            }
        )

        return redirect('success')

    return render(request, 'home.html', {'current_date': current_date})


@login_required
def admin_download_timesheets(request):
    if not request.user.is_staff:
        raise PermissionDenied("You do not have permission to download timesheets.")

    file_to_download = request.GET.get('user')
    if file_to_download:
        target_user = User.objects.get(username=file_to_download)
        profile = UserProfile.objects.get(user=target_user)

        # ✅ GET ALL DATA DIRECTLY FROM NEON DATABASE
        entries = TimesheetEntry.objects.filter(user=target_user).order_by('date')

        # ✅ GENERATE EXCEL 100% IN MEMORY. NOTHING SAVED TO DISK.
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(['Date', 'Project Working On', 'Log In Time', 'Log Out Time', 'Hours Worked'])

        for entry in entries:
            ws.append([
                str(entry.date),
                entry.project,
                entry.login_time,
                entry.logout_time,
                entry.hours_worked
            ])

        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)

        filename = f"{profile.employee_name} Timesheet.xlsx"
        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    profiles = UserProfile.objects.all()
    excel_files = []
    for profile in profiles:
        entry_count = TimesheetEntry.objects.filter(user=profile.user).count()
        if entry_count > 0:
            excel_files.append({
                'name': f"{profile.employee_name} ({entry_count} entries)",
                'url': f'/download-timesheets/?user={profile.user.username}'
            })

    return render(request, 'download_timesheets.html', {'excel_files': excel_files})


def logout_view(request):
    logout(request)
    return redirect('login')

def success_view(request):
    return render(request, 'success.html')

@login_required
def password_change_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            storage = messages.get_messages(request)
            for _ in storage:
                pass
            messages.success(request, 'Your password has been updated!')
            logout(request)
            return redirect('password_change_done')
        else:
            logger.error(f"Password change form errors: {form.errors}")
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'password_change_form.html', {'form': form})

def password_change_done(request):
    return render(request, 'password_change_done.html')
