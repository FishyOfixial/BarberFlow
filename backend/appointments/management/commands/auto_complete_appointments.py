from django.core.management.base import BaseCommand
from django.utils.timezone import now
from datetime import timedelta

from appointments.models import Appointment


class Command(BaseCommand):
    help = "Automatically complete overdue appointments"

    def handle(self, *args, **kwargs):
        limit_time = now() - timedelta(minutes=30)

        appointments = Appointment.objects.filter(
            status__in=["pending", "in_progress"],
            end_datetime__lte=limit_time,
        )

        count = appointments.update(status="completed")

        self.stdout.write(
            self.style.SUCCESS(f"{count} appointments auto-completed")
        )
