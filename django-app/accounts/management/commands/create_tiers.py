from django.core.management import BaseCommand
from accounts.models import AccountTier, ThumbnailSizes
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = "Create basic tiers nad superuser only if it doesn't exists"

    def handle(self, *args, **options):
        if AccountTier.objects.filter(name='Basic').exists() or AccountTier.objects.filter(name='Premium').exists():
            return

        size_200 = ThumbnailSizes(thumbnail_size=200)
        size_400 = ThumbnailSizes(thumbnail_size=400)
        size_200.save()
        size_400.save()

        basic = AccountTier(name='Basic', original_link=False, expiring_link=False)
        basic.save()
        basic.sizes.add(size_200)

        premium = AccountTier(name='Premium', original_link=True, expiring_link=False)
        premium.save()
        premium.sizes.add(size_200)
        premium.sizes.add(size_400)

        enterprise = AccountTier(name='Enterprise', original_link=True, expiring_link=True)
        enterprise.save()
        enterprise.sizes.add(size_200)
        enterprise.sizes.add(size_400)

        User = get_user_model()
        user = User.objects.create_superuser(username='admin', password='admin', email='admin@admin.pl')
        user.account_tier = enterprise
        user.save()
