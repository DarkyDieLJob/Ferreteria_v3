from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from allauth.socialaccount.models import SocialAccount
from django.db.models import Q

class Command(BaseCommand):
    help = 'Remove SocialAccount entries that have no associated User'

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Find all SocialAccount entries where the user doesn't exist or is None
        count = 0
        for social_account in SocialAccount.objects.all():
            try:
                # Check if user is None or doesn't exist
                if social_account.user is None:
                    raise User.DoesNotExist("User is None")
                # This will raise User.DoesNotExist if user doesn't exist
                social_account.user
            except (User.DoesNotExist, AttributeError) as e:
                self.stdout.write(
                    self.style.WARNING(f'Removing orphaned SocialAccount (ID: {social_account.id}): {social_account} - Reason: {str(e)}')
                )
                social_account.delete()
                count += 1
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No orphaned SocialAccount records found.'))
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully removed {count} orphaned SocialAccount records.')
            )
