from rest_framework import permissions


class AuthorOrModeratorOrAdmin(permissions.BasePermission):
    """
    Разрешение на редактирование авторам контента, модераторам или админам.
    """

    def has_object_permission(self, request, view, obj):
        return ((request.method in permissions.SAFE_METHODS)
                or obj.author == request.user
                or (request.user.is_authenticated
                    and request.user.access_administrator)
                or (request.user.is_authenticated
                    and request.user.access_moderator))


class AdminOrReadOnly(permissions.BasePermission):
    """
    Права доступа администратора и
    чтения всеми пользователями.
    """

    message = 'You must have admin rights to perform this action.'

    def has_permission(self, request, view):
        return ((request.method in permissions.SAFE_METHODS)
                or (request.user.is_authenticated
                    and request.user.access_administrator
                    ))


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated
                and (request.user.access_administrator
                     or request.user.is_superuser))
