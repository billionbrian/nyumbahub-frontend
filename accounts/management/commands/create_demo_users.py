from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Creates or updates development demo users (demo_landlord and demo_tenant) for local testing."

    def handle(self, *args, **options):
        demo_accounts = [
            {
                "username": "demo_landlord",
                "email": "demo_landlord@tapin.test",
                "password": "DemoLandlord123!",
                "role": "landlord",
                "phone": "+254700000001",
                "first_name": "Demo",
                "last_name": "Landlord",
                "email_verified": True,
            },
            {
                "username": "demo_tenant",
                "email": "demo_tenant@tapin.test",
                "password": "DemoTenant123!",
                "role": "tenant",
                "phone": "+254700000002",
                "first_name": "Demo",
                "last_name": "Tenant",
                "email_verified": True,
            },
        ]

        self.stdout.write(self.style.WARNING("=================================================="))
        self.stdout.write(self.style.WARNING("   TapIn Development Demo User Provisioning   "))
        self.stdout.write(self.style.WARNING("=================================================="))

        for account in demo_accounts:
            user = User.objects.filter(username=account["username"]).first()
            if not user:
                # Check if email is already in use by another user
                existing_email_user = User.objects.filter(email=account["email"]).first()
                if existing_email_user:
                    user = existing_email_user
                    user.username = account["username"]
                else:
                    user = User(
                        username=account["username"],
                        email=account["email"],
                    )
            
            # Apply attributes
            user.email = account["email"]
            user.role = account["role"]
            user.phone = account["phone"]
            user.first_name = account["first_name"]
            user.last_name = account["last_name"]
            user.email_verified = account["email_verified"]
            user.is_staff = False
            user.is_superuser = False
            user.is_active = True
            user.set_password(account["password"])
            user.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ Provisioned demo user '{user.username}':\n"
                    f"    Role:     {user.role}\n"
                    f"    Email:    {user.email}\n"
                    f"    Password: {account['password']}\n"
                )
            )

        self.stdout.write(self.style.WARNING("NOTE: These accounts are for development/testing only."))
        self.stdout.write(self.style.SUCCESS("Demo users provisioned successfully."))
