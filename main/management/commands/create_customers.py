# your_app/management/commands/create_customers.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from authentication.models import Customer

class Command(BaseCommand):
    help = 'Ensure every User has a corresponding Customer'

    def handle(self, *args, **kwargs):
        for user in User.objects.all():
            if not hasattr(user, 'customer'):
                # Create a Customer instance for each User
                Customer.objects.get_or_create(
                    user=user,
                    full_name=user.get_full_name(),
                    email=user.email
                    # Populate other fields as necessary
                )
        self.stdout.write(self.style.SUCCESS('Successfully created Customer instances for all Users'))
