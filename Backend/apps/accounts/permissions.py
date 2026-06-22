from rest_framework import permissions


class IsOrganizationAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (user.is_superuser or user.role == "admin")
        )

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_superuser:
            return True

        organization = getattr(obj, "organization", obj)
        return organization == user.organization
