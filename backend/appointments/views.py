from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .permissions import CanCancelAppointment, CanCompleteAppointment


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
