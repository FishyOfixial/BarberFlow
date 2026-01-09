from datetime import timedelta
from django.utils.timezone import make_aware
from django.db.models import Q
from .models import Barber, Appointment, BarberSchedule

def barber_has_conflict(barber, start_datetime, end_datetime, exclude_appointment_id=None):
    qs = Appointment.objects.filter(
        barber=barber,
        start_datetime__lt=end_datetime,
        end_datetime__gt=start_datetime,
        status__in=["pending", "in_progress"],
    )

    if exclude_appointment_id:
        qs = qs.exclude(id=exclude_appointment_id)

    return qs.exists()


def assign_available_barber(service, start_datetime):
    end_datetime = start_datetime + timedelta(
        minutes=service.duration_minutes
    )

    weekday = start_datetime.weekday()

    barbers = Barber.objects.filter(
        is_active=True,
        services=service
    )

    for barber in barbers:
        try:
            schedule = BarberSchedule.objects.get(
                barber=barber,
                day_of_week=weekday
            )
        except BarberSchedule.DoesNotExist:
            continue

        if not (
            schedule.start_time <= start_datetime.time()
            and schedule.end_time >= end_datetime.time()
        ):
            continue

        if barber_has_conflict(barber, start_datetime, end_datetime):
            continue

        return barber

    return None
