from django.core.management.base import BaseCommand
from user.models import UserProfile
from django.conf import settings
from decouple import config

class Command(BaseCommand):
    help = 'Creates a superuser if none exists'

    def handle(self, *args, **options):
        username = config('DJANGO_SUPERUSER_USERNAME', 'admin@gmail.com')
        email = config('DJANGO_SUPERUSER_EMAIL', 'admin@gmail.com')
        password = config('DJANGO_SUPERUSER_PASSWORD', 'Adminpass111111@')

        if not UserProfile.objects.filter(username=username).exists():
            self.stdout.write('Creating superuser...')
            user = UserProfile.objects.create_superuser(
                username=username,
                email=email,
                password=password,
            )
            # token = Token.objects.create(user=user)
            self.stdout.write(self.style.SUCCESS('Superuser created successfully'))