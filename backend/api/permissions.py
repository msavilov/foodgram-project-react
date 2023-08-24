from rest_framework.permissions import SAFE_METHODS, BasePermission


class AdminOrReadOnly(BasePermission):
    """Права доступа для администраторов"""
    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS
                or request.user and request.user.is_superuser)


class AuthorOrReadOnly(BasePermission):
    """Права доступа для авторов"""
    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS
                or request.user == obj.author)


class AdminOrAuthor(BasePermission):
    """Права доступа для автора или администраторов"""
    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS
                or request.user == obj.author or request.user.is_superuser)
