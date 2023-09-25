from django.contrib import admin

# Register your models here.
from .models import AccountTier, CustomUser, OriginalImage, ExpiringLink, ThumbnailSizes, ImageVersion

admin.site.register(AccountTier)
admin.site.register(CustomUser)
admin.site.register(OriginalImage)
admin.site.register(ImageVersion)
admin.site.register(ExpiringLink)
admin.site.register(ThumbnailSizes)
