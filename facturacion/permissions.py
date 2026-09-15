from rest_framework import permissions


class EsPropietario(permissions.BasePermission):
    """
    Permiso que solo permite al propietario del objeto verlo o modificarlo.
    """
    
    def has_object_permission(self, request, view, obj):
        # El usuario debe ser el propietario
        return obj.propietario == request.user