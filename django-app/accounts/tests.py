from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from accounts.models import OriginalImage, AccountTier
from django.core.files.images import ImageFile
from PIL import Image
import io


class UserAuthenticationTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.username = 'admin'
        cls.password = 'admin'
        cls.email = 'admin'
        cls.user = get_user_model().objects.create_user(username=cls.username, password=cls.password,
                                                        email=cls.email)

    def test_login(self):
        response = self.client.post(
            reverse('rest_framework:login'), {'username': self.username, 'password': self.password})
        self.assertEqual(response.status_code, 302)

    def test_logout(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('rest_framework:logout'))
        self.assertEqual(response.status_code, 200)

    def test_failed_login(self):
        response = self.client.post(reverse('rest_framework:login'),
                                    {'username': 'wronguser', 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please enter a correct username and password')


class ImageUploadsTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        call_command('create_tiers')
        im = Image.new('RGBA', size=(50, 50), color=(256, 0, 0))
        img_bytes = io.BytesIO()
        im.save(img_bytes, format='png')
        cls.image = ImageFile(io.BytesIO(img_bytes.getvalue()), name='test.png')
        cls.user = get_user_model().objects.get(username='admin')

    def relog_user(self, tier='Enterprise'):
        self.client.logout()
        user = get_user_model().objects.create_user(username='test', password='test', email='test@test.pl')
        user.account_tier = AccountTier.objects.get(name=tier)
        user.save()
        self.client.login(username='test', password='test')

    def setUp(self):
        self.client.login(username='admin', password='admin')

    def createImage(self):
        self.img = OriginalImage(owner=self.user, file=self.image)
        self.img.save()

    def test_image_view(self):
        response = self.client.post(reverse('accounts:image'), {'file': self.image})
        self.assertEqual(response.status_code, 201)
        get_response = self.client.get(reverse('accounts:image'))
        self.assertEqual(response.data.get('file'), get_response.data[0].get('file'))
        self.assertEqual(response.data.get('thumbnails'), get_response.data[0].get('thumbnails'))
        OriginalImage.objects.get(id=response.data.get('id')).delete()

    def test_protected_image(self):
        self.createImage()
        get_response = self.client.get(reverse('protected_image', kwargs={"file": self.img.file}))
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response.headers['Content-Type'], 'image/jpeg')
        self.img.delete()

    def test_forbidden_access_image(self):
        self.createImage()
        self.relog_user()
        get_response = self.client.get(reverse('protected_image', kwargs={"file": self.img.file}))
        self.assertEqual(get_response.status_code, 403)
        self.img.delete()

    def test_expiring_link(self):
        self.createImage()
        response = self.client.post(reverse('accounts:link'), {'file': self.img.file.name, 'seconds': 600})
        self.assertEqual(response.status_code, 200)
        link = response.data.get('link').split('/')[-2]
        response = self.client.get(reverse('accounts:link', kwargs={"file": link}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'image/jpeg')
        self.img.delete()

    def test_expiring_link_less_seconds(self):
        self.createImage()
        response = self.client.post(reverse('accounts:link'), {'file': self.img.file.name, 'seconds': 50})
        self.assertEqual(response.status_code, 400)
        self.img.delete()