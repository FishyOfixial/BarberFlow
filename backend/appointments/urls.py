from rest_framework.routers import DefaultRouter
from .views import AppointmentViewSet, ServiceViewSet, BarberViewSet

router = DefaultRouter()
router.register("appointments", AppointmentViewSet, basename="appointment")
router.register("services", ServiceViewSet, basename="service")
router.register("barbers", BarberViewSet, basename="barber")

urlpatterns = router.urls
