from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from properties.models import Property, PropertyOwnership
from expenses.models import Expense
from labor.models import Labor
import datetime

User = get_user_model()


class Command(BaseCommand):
    help = "Seed the database with dummy data for development"

    def handle(self, *args, **options):
        self.stdout.write("Seeding database...")

        # Users
        nick, _ = User.objects.get_or_create(username="nick")
        nick.set_password("password123")
        nick.save()

        sarah, _ = User.objects.get_or_create(username="sarah")
        sarah.set_password("password123")
        sarah.save()

        # Property
        prop, _ = Property.objects.get_or_create(
            address="123 Main St",
            defaults={
                "purchase_price": 400000,
                "purchase_date": datetime.date(2024, 1, 15),
            }
        )

        # Ownerships
        PropertyOwnership.objects.get_or_create(
            user=nick, property=prop,
            defaults={"initial_contribution": 250000, "joined_at": datetime.date(2024, 1, 15)}
        )
        PropertyOwnership.objects.get_or_create(
            user=sarah, property=prop,
            defaults={"initial_contribution": 150000, "joined_at": datetime.date(2024, 1, 15)}
        )

        # Expenses
        Expense.objects.get_or_create(
            property=prop, paid_by=nick, amount=5000, date=datetime.date(2024, 3, 1),
            defaults={"category": "repair", "description": "Roof repair"}
        )
        Expense.objects.get_or_create(
            property=prop, paid_by=sarah, amount=2000, date=datetime.date(2024, 4, 1),
            defaults={"category": "improvement", "description": "New flooring"}
        )

        # Labor
        Labor.objects.get_or_create(
            property=prop, performed_by=nick, date=datetime.date(2024, 3, 15),
            defaults={"hours": 20, "hourly_rate": 50, "description": "Painting"}
        )
        Labor.objects.get_or_create(
            property=prop, performed_by=sarah, date=datetime.date(2024, 4, 10),
            defaults={"hours": 10, "hourly_rate": 75, "description": "Electrical work"}
        )

        self.stdout.write(self.style.SUCCESS("Done."))
