from django.core.files.images import ImageFile
from rest_framework import serializers
from .models import OriginalImage, ImageVersion
from PIL import Image
import io


class ImageVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageVersion
        fields = ["file", "height"]


class ImageSerializer(serializers.ModelSerializer):
    thumbnails = ImageVersionSerializer(many=True, read_only=True)

    class Meta:
        model = OriginalImage
        fields = ["file", "id", "thumbnails"]

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        instance = super(ImageSerializer, self).create(validated_data)
        sizes = self.context['request'].user.account_tier.sizes.all()

        for size in sizes:
            im = Image.open(instance.file.path)
            im.thumbnail((im.width, size.thumbnail_size))
            img_bytes = io.BytesIO()
            im.save(img_bytes, format=im.format)
            image = ImageFile(io.BytesIO(img_bytes.getvalue()), name=instance.file.name)
            ImageVersion(original_image=instance, file=image, height=size.thumbnail_size).save()

        return instance

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if not self.context['request'].user.account_tier.original_link:
            data.pop('file')
        return data

