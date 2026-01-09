from rest_framework import serializers
from django.utils.timezone import now

from .models import Barber, Service, Appointment
from .services import assign_available_barber


class BarberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Barber
        fields = ["id", "user", "is_active"]

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ["id", "name", "duration_minutes"]


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = [
            "id",
            "service",
            "start_datetime",
            "end_datetime",
            "status",
        ]
        read_only_fields = ["end_datetime", "status"]

    def validate_start_datetime(self, value):
        if value < now():
            raise serializers.ValidationError(
                "Cannot create an appointment in the past."
            )
        return value

    def create(self, validated_data):
        request = self.context["request"]
        client = request.user

        service = validated_data["service"]
        start_datetime = validated_data["start_datetime"]

        barber = assign_available_barber(service, start_datetime)
        if not barber:
            raise serializers.ValidationError(
                "No available barber for this time."
            )

        appointment = Appointment.objects.create(
            client=client,
            barber=barber,
            service=service,
            start_datetime=start_datetime,
        )

        return appointment
