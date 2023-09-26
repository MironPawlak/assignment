# Create your views here.
import os, datetime

from rest_framework.views import APIView
from django.conf import settings
from django.http import HttpResponse, Http404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django.urls import reverse
from .serializers import ImageSerializer, ExpiringLinkSerializer, ExpiringLinkDataSerializer
from .models import OriginalImage, ImageVersion, ExpiringLink
from .permissions import OwnImagePermission, AccountTierPermission, ExpiringLinkPermissionOrReadOnly
from django.utils.crypto import get_random_string
from django.utils import timezone


class ImageAPIView(generics.ListCreateAPIView):
    serializer_class = ImageSerializer
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        return OriginalImage.objects.filter(owner=self.request.user)


class ProtectedImageView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, OwnImagePermission, AccountTierPermission]

    def get(self, request, file):
        media_path = os.path.join(settings.MEDIA_ROOT, file)
        try:
            with open(media_path, 'rb') as file:
                return HttpResponse(file.read(), content_type="image/jpeg")
        except OSError:
            raise Http404


class LinkView(generics.GenericAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly, ExpiringLinkPermissionOrReadOnly]
    serializer_class = ExpiringLinkDataSerializer

    def post(self, request, file='None'):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = {
            'file': serializer.validated_data['file'],
            'link': get_random_string(20),
            'expiring': timezone.now() + datetime.timedelta(seconds=serializer.validated_data['seconds'])
        }
        serializer_save = ExpiringLinkSerializer(data=data)
        serializer_save.is_valid(raise_exception=True)
        serializer_save.save()
        return Response(
            {'link': request.build_absolute_uri(reverse('accounts:link',
                                                        kwargs={"file": serializer_save.validated_data['link']}))})

    def get(self, request, file='None'):
        link = ExpiringLink.objects.filter(link=file).first()
        if not link:
            raise Http404
        if link.expiring < timezone.now():
            link.delete()
            raise Http404
        media_path = os.path.join(settings.MEDIA_ROOT, link.file)
        try:
            with open(media_path, 'rb') as file:
                return HttpResponse(file.read(), content_type="image/jpeg")
        except OSError:
            raise Http404

