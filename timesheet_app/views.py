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
    # Check if the logged-in user is an admin (staff)
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
            excel_filename = f'{EXCEL_PATH}{employee_name}.xlsx'
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.append(['Date', 'Project Working On', 'Log In Time', 'Log Out Time', 'Hours Worked'])  # Add headings
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
    current_date = timezone.now().date()  # Get the current date

    if request.method == 'POST':
        project = request.POST['project']
        date = request.POST['date']
        login_time = request.POST['login_time']
        logout_time = request.POST['logout_time']

        # Convert login and logout time strings to datetime objects
        login_time_obj = datetime.strptime(login_time, '%H:%M')
        logout_time_obj = datetime.strptime(logout_time, '%H:%M')

        # Calculate the number of hours worked (difference between logout and login times)
        hours_worked = (logout_time_obj - login_time_obj).seconds / 3600  # Convert seconds to hours
        formatted_hours_worked = format_hours_and_minutes(hours_worked)  # Format to "Xh Ym"

        profile = UserProfile.objects.get(user=request.user)
        excel_filename = f'{EXCEL_PATH}{profile.employee_name}.xlsx'

        # Load or create the workbook
        if os.path.exists(excel_filename):
            wb = openpyxl.load_workbook(excel_filename)
        else:
            wb = openpyxl.Workbook()

        ws = wb.active

        # Add a heading row if it's a new file or missing headers
        if ws.max_row == 1 and ws[1][0].value is None:
            ws.append(['Date', 'Project Working On', 'Log In Time', 'Log Out Time', 'Hours Worked'])

        # Check if the date already exists in the Excel sheet
        for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
            if row[0].value == date:
                row[1].value = project
                row[2].value = login_time
                row[3].value = logout_time
                row[4].value = formatted_hours_worked  # Update hours worked if the entry exists
                break
        else:
            # Append a new entry with formatted hours worked
            ws.append([date, project, login_time, logout_time, formatted_hours_worked])

        wb.save(excel_filename)

        return redirect('success')  # Redirect to success page after submission

    return render(request, 'home.html', {'current_date': current_date})

@login_required
def download_timesheet(request):
    profile = UserProfile.objects.get(user=request.user)
    excel_filename = f'{EXCEL_PATH}{profile.employee_name}.xlsx'

    # Check if the file exists
    if os.path.exists(excel_filename):
        return FileResponse(open(excel_filename, 'rb'), as_attachment=True, filename=f"{profile.employee_name}_timesheet.xlsx")
    else:
        return render(request, 'error.html', {'message': 'Timesheet file not found.'})

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

            # Clear any existing messages to avoid multiple success messages
            storage = messages.get_messages(request)
            for _ in storage:
                pass  # This clears existing messages

            messages.success(request, 'Your password has been updated!')

            # Log out the user after successful password change and redirect to password change done
            logout(request)
            return redirect('password_change_done')
        else:
            print(form.errors)  # For debugging purposes if the form is invalid
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'password_change_form.html', {'form': form})

# No login required for password_change_done
def password_change_done(request):
    return render(request, 'password_change_done.html')
