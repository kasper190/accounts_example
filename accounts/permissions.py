from rest_framework.permissions import (
    BasePermission,
    SAFE_METHODS,
)


class IsAuthenticatedAndActive(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_active


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.id == request.user.id


class IsOwnerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.id == int(view.kwargs['pk']) or request.user.is_admin


class IsOwnerOrAdminObject(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.id == request.user.id or request.user.is_admin
