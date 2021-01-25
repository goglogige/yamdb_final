from rest_framework.permissions import SAFE_METHODS, BasePermission

from .models import UserRole


class IsAdministrator(BasePermission):
    message = "You can't do this!"

    def has_permission(self, request, view):
        return (request.user.is_authenticated and (
                request.user.get_role == UserRole.ADMIN or
                request.user.is_staff or
                request.user.is_superuser
                ))


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class IsAuthorOrIsStaffPermission(BasePermission):
    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS and
                request.user.is_anonymous or
                request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in ['PATCH', 'DELETE']:
            return (obj.author == request.user or
                    request.user.is_staff or
                    request.user.is_superuser or
                    request.user.get_role in [
                        UserRole.ADMIN,
                        UserRole.MODERATOR
                    ])
        return True
