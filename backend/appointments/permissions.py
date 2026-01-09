from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.utils.timezone import now


class CanCancelAppointment(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method != "DELETE":
            return True

        user = request.user

        if user.role != "client":
            return False

        if obj.client != user:
            return False

        if obj.start_datetime <= now():
            return False

        return True


class CanCompleteAppointment(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method not in ["PATCH", "PUT"]:
            return True

        user = request.user

        if user.role != "barber":
            return False

        if not obj.barber or obj.barber.user != user:
            return False

        if obj.status != "in_progress":
            return False

        return True
