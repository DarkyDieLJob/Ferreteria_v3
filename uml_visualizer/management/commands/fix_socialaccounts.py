from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from allauth.socialaccount.models import SocialAccount
from django.db import transaction

class Command(BaseCommand):
    help = 'Comprehensive cleanup of SocialAccount records to fix related issues'

    def handle(self, *args, **options):
        User = get_user_model()
        count = 0
        
        with transaction.atomic():
            # Get all social accounts
            for sa in SocialAccount.objects.all():
                try:
                    # Try to access the user to trigger any related errors
                    user = sa.user
                    if not user:
                        raise User.DoesNotExist("User is None")
                    
                    # If we get here, the user exists and is accessible
                    self.stdout.write(
                        self.style.SUCCESS(f'SocialAccount {sa.id} is valid (user: {user.username})')
                    )
                    
                except Exception as e:
                    # Log the error and delete the problematic record
                    self.stdout.write(
                        self.style.ERROR(f'Error with SocialAccount {sa.id}: {str(e)}')
                    )
                    self.stdout.write(
                        self.style.WARNING(f'Deleting problematic SocialAccount: {sa}')
                    )
                    sa.delete()
                    count += 1
            
            if count == 0:
                self.stdout.write(
                    self.style.SUCCESS('No problematic SocialAccount records found.')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully removed {count} problematic SocialAccount records.')
                )
