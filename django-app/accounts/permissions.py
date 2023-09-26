from rest_framework import permissions
from .models import OriginalImage, ImageVersion


class OwnImagePermission(permissions.BasePermission):
    """
    Permission allowing only to view own images
    """

    def has_permission(self, request, view):
        image = OriginalImage.objects.filter(file=view.kwargs.get('file')).first() or ImageVersion.objects.filter(
            file=view.kwargs.get('file')).first()
        if image:
            if hasattr(image, 'owner'):
                return image.owner == request.user
            else:
                return image.original_image.owner == request.user
        return False


class AccountTierPermission(permissions.BasePermission):
    """
    Permission allowing only to see images appropriate to the tier of account
    """

    def has_permission(self, request, view):
        image = OriginalImage.objects.filter(file=view.kwargs.get('file')).first()
        if image:
            return request.user.account_tier.original_link
        return True


class ExpiringLinkPermissionOrReadOnly:
    """
    Permission allowing to create expiring links or seeing image
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.account_tier.expiring_link
