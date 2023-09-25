# Create your views here.
import os, datetime

from rest_framework.views import APIView
from django.conf import settings
from django.http import HttpResponse, Http404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django.urls import reverse
from .serializers import ImageSerializer
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


class LinkView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly, ExpiringLinkPermissionOrReadOnly]

    def post(self, request, file, seconds='None'):
        image = OriginalImage.objects.filter(file=file).first() or ImageVersion.objects.filter(
            file=file).first()
        if not image or not seconds:
            raise Http404

        link = get_random_string(20)
        expiring = timezone.now() + datetime.timedelta(seconds=int(seconds))
        instance = ExpiringLink(file=file, link=link, expiring=expiring)
        instance.save()
        data = {
            'link': request.build_absolute_uri(reverse('link', kwargs={"file": link}))
        }
        return Response(data)

    def get(self, request, file, seconds='None'):
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

