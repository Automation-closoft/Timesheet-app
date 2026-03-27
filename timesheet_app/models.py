from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_name = models.CharField(max_length=100)

    def __str__(self):
        return self.employee_name

# THIS IS THE IMPORTANT NEW MODEL
class TimesheetEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    project = models.CharField(max_length=200)
    login_time = models.CharField(max_length=10)
    logout_time = models.CharField(max_length=10)
    hours_worked = models.CharField(max_length=20)

    class Meta:
        unique_together = ['user', 'date']
        ordering = ['date']
