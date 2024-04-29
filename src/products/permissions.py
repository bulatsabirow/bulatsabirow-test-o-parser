from rest_framework import permissions


class ProductsPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action == "create":
            return request.user.is_authenticated and request.user.telegram_id
        super().has_permission(request, view)
