from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    """A management command to create the initial Admin user.

    Usage:
        python manage.py create_admin --username=admin --email=admin@example.com --password=SecureAdminPassword123 --first_name=Admin --last_name=User
    """

    help = "Creates an admin user"

    def add_arguments(self, parser):
        parser.add_argument("--username", required=True, help="Admin username")
        parser.add_argument("--email", required=True, help="Admin email")
        parser.add_argument("--password", required=True, help="Admin password")
        parser.add_argument("--first_name", default="Admin", help="Admin first name")
        parser.add_argument("--last_name", default="User", help="Admin last name")

    def handle(self, *args, **options):
        username = options["username"]
        email = options["email"]
        password = options["password"]
        first_name = options["first_name"]
        last_name = options["last_name"]

        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f"User with username {username} already exists")
            )
            return

        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.WARNING(f"User with email {email} already exists")
            )
            return

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=User.ADMIN,
            is_staff=True,
            is_superuser=True,
        )

        self.stdout.write(self.style.SUCCESS(f"Admin user created: {user.username}"))
