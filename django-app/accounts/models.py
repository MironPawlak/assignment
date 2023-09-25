import os
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.db import models
from django.dispatch import receiver


class ThumbnailSizes(models.Model):
    thumbnail_size = models.IntegerField()

    def __str__(self):
        return str(self.thumbnail_size)


class AccountTier(models.Model):
    name = models.CharField(max_length=128)
    original_link = models.BooleanField()
    expiring_link = models.BooleanField()
    sizes = models.ManyToManyField(ThumbnailSizes)

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    account_tier = models.ForeignKey(AccountTier, on_delete=models.DO_NOTHING, null=True, blank=True)


class OriginalImage(models.Model):
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    file = models.ImageField(validators=[FileExtensionValidator(allowed_extensions=["png", "jpg"])])


class ImageVersion(models.Model):
    original_image = models.ForeignKey(OriginalImage, related_name='thumbnails', on_delete=models.CASCADE)
    height = models.IntegerField()
    file = models.ImageField(validators=[FileExtensionValidator(allowed_extensions=["png", "jpg"])])


class ExpiringLink(models.Model):
    file = models.CharField(max_length=1024)
    link = models.CharField(max_length=1024)
    expiring = models.DateTimeField()


@receiver(models.signals.post_delete, sender=OriginalImage)
@receiver(models.signals.post_delete, sender=ImageVersion)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem when
    Image is deleted e.g from Django admin
    """
    try:
        os.remove(instance.file.path)
    except FileNotFoundError:
        pass