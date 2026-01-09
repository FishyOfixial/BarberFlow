from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .permissions import CanCancelAppointment, CanCompleteAppointment
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import now


from .models import Appointment, Service, Barber
from .serializers import (
    AppointmentSerializer,
    ServiceSerializer,
    BarberSerializer,
)


class ServiceViewSet(ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]


class BarberViewSet(ModelViewSet):
    queryset = Barber.objects.filter(is_active=True)
    serializer_class = BarberSerializer
    permission_classes = [IsAuthenticated]


class AppointmentViewSet(ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [
        IsAuthenticated,
        CanCancelAppointment,
        CanCompleteAppointment,
    ]

    def get_queryset(self):
        user = self.request.user

        if user.role == "admin":
            return Appointment.objects.all()

        if user.role == "barber":
            return Appointment.objects.filter(barber__user=user)

        return Appointment.objects.filter(client=user)

    def perform_create(self, serializer):
        serializer.save()


    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        appointment = self.get_object()

        if not appointment.can_be_cancelled():
            return Response(
                {"detail": "This appointment cannot be cancelled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        appointment.status = "cancelled"
        appointment.save()

        return Response(
            {"detail": "Appointment cancelled successfully."}
        )


    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        appointment = self.get_object()

        if appointment.status != "in_progress":
            return Response(
                {"detail": "Appointment is not in progress."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        appointment.status = "completed"
        appointment.save()

        return Response(
            {"detail": "Appointment completed successfully."}
        )
