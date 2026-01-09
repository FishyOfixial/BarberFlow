from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from datetime import datetime, time, timedelta

User = settings.AUTH_USER_MODEL

class Barber(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Barber: {self.user.username}"
    
class BarberSchedule(models.Model):
    WEEK_DAYS = (
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    )

    barber = models.ForeignKey(Barber, on_delete=models.CASCADE, related_name='schedules')
    day_of_week = models.IntegerField(choices=WEEK_DAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        unique_together = ('barber', 'day_of_week')
    
    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError("Start time must be before end time.")
        
        if self.start_time < time(7, 0):
            raise ValidationError("Barber schedule cannot start before 7:00 AM.")
        
        if self.end_time > time(20, 0):
            raise ValidationError("Barber schedule cannot go past 8:00 PM.")
        
    def get_day_of_week_display(self):
        return f"{self.WEEK_DAYS[self.day_of_week]}: {self.start_time} - {self.end_time}"

    def __str__(self):
        return f"{self.barber} - {self.get_day_of_week_display()}"
    

class Service(models.Model):
    name = models.CharField(max_length=100)
    duration_minutes = models.PositiveIntegerField()
    barbers = models.ManyToManyField(Barber, related_name='services')

    def clean(self):
        if self.duration_minutes <= 0:
            raise ValidationError("Service duration must be greater than 0.")
        
    def __str__(self):
        return self.name
    

class Appointment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    barber = models.ForeignKey(Barber, on_delete=models.SET_NULL, null=True, blank=True)

    service = models.ForeignKey(Service, on_delete=models.PROTECT)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField(editable=False)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        self.end_datetime = self.start_datetime + timedelta(minutes=self.service.duration_minutes)

        if self.end_datetime.time() > time(20, 0):
            raise ValidationError('Appointment must end before 8:00 PM.')
        
        if self.start_datetime < datetime.now():
            raise ValidationError('Cannot create appointments in the past.')
        
        if self.barber:
            overlapping = Appointment.objects.filter(
                barber=self.barber,
                start_datetime__lt=self.end_datetime,
                end_datetime__gt=self.start_datetime,
            ).exclude(id=self.id)

            if overlapping.exists():
                raise ValidationError("Barber is not available at this time.")
            
    def can_be_cancelled(self):
        return (
            self.start_datetime > datetime.now() and self.status not in ['completed', 'cancelled']
        )
    
    def __str__(self):
        return f'Appointment - {self.client} - {self.start_datetime}'