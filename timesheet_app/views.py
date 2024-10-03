from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.utils import timezone
from .models import UserProfile
from .forms import UserRegistrationForm
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.http import FileResponse
import openpyxl
import os
from datetime import datetime

# Path to save Excel files
EXCEL_PATH = 'timesheets/'

# Ensure the path exists
if not os.path.exists(EXCEL_PATH):
    os.makedirs(EXCEL_PATH)

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
            profile = UserProfile.objects.create(user=user, employee_name=employee_name)

            # Create a new Excel sheet for the user
            excel_filename = os.path.join(EXCEL_PATH, f'{employee_name}.xlsx')
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.append(['Date', 'Project Working On', 'Log In Time', 'Log Out Time', 'Hours Worked'])
            wb.save(excel_filename)

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
        project = request.POST['project']
        date = request.POST['date']
        login_time = request.POST['login_time']
        logout_time = request.POST['logout_time']

        login_time_obj = datetime.strptime(login_time, '%H:%M')
        logout_time_obj = datetime.strptime(logout_time, '%H:%M')

        hours_worked = (logout_time_obj - login_time_obj).seconds / 3600
        formatted_hours_worked = format_hours_and_minutes(hours_worked)

        profile = UserProfile.objects.get(user=request.user)
        excel_filename = os.path.join(EXCEL_PATH, f'{profile.employee_name}.xlsx')

        if os.path.exists(excel_filename):
            wb = openpyxl.load_workbook(excel_filename)
        else:
            wb = openpyxl.Workbook()

        ws = wb.active

        if ws.max_row == 1 and ws[1][0].value is None:
            ws.append(['Date', 'Project Working On', 'Log In Time', 'Log Out Time', 'Hours Worked'])

        for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
            if row[0].value == date:
                row[1].value = project
                row[2].value = login_time
                row[3].value = logout_time
                row[4].value = formatted_hours_worked
                break
        else:
            ws.append([date, project, login_time, logout_time, formatted_hours_worked])

        wb.save(excel_filename)
        return redirect('success')

    return render(request, 'home.html', {'current_date': current_date})

@login_required
def admin_download_timesheets(request):
    if not request.user.is_staff:
        raise PermissionDenied("You do not have permission to download timesheets.")

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(['Employee Name', 'Date', 'Project Working On', 'Log In Time', 'Log Out Time', 'Hours Worked'])

    for profile in UserProfile.objects.all():
        excel_filename = os.path.join(EXCEL_PATH, f'{profile.employee_name}.xlsx')
        if os.path.exists(excel_filename):
            wb_user = openpyxl.load_workbook(excel_filename)
            ws_user = wb_user.active

            for row in ws_user.iter_rows(min_row=2, values_only=True):
                ws.append([profile.employee_name] + list(row))

    all_timesheets_filename = os.path.join(EXCEL_PATH, 'all_timesheets.xlsx')
    wb.save(all_timesheets_filename)

    response = FileResponse(open(all_timesheets_filename, 'rb'), as_attachment=True, filename='all_timesheets.xlsx')

    os.remove(all_timesheets_filename)

    return response

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
            print(form.errors)
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'password_change_form.html', {'form': form})

def password_change_done(request):
    return render(request, 'password_change_done.html')
