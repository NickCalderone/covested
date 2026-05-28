# calculate equity percentage for each owner based on their contributions vs total property value
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from properties.models import Property, PropertyOwnership
from expenses.models import Expense
from labor.models import Labor
from properties.services import calculate_equity
import datetime

User = get_user_model()


class CalculateEquityTests(TestCase):

    def setUp(self):
        # users
        self.nick = User.objects.create_user(username="nick", password="pass")
        self.sarah = User.objects.create_user(username="sarah", password="pass")

		# propery
        self.prop = Property.objects.create(
            address="123 Main St",
            purchase_price=Decimal("400000"),
            purchase_date=datetime.date(2024, 1, 1),
        )

		# property ownerships
        PropertyOwnership.objects.create(
            user=self.nick, property=self.prop,
            initial_contribution=Decimal("200000"),
            joined_at=datetime.date(2024, 1, 1),
        )
        PropertyOwnership.objects.create(
            user=self.sarah, property=self.prop,
            initial_contribution=Decimal("200000"),
            joined_at=datetime.date(2024, 1, 1),
        )

	# check that with equal contributions, equity is 50/50
    def test_equal_contributions(self):
        equity = calculate_equity(self.prop)
        self.assertEqual(equity[self.nick.id], Decimal("50.0000"))
        self.assertEqual(equity[self.sarah.id], Decimal("50.0000"))

	# check that if one owner pays an expense, their equity increases
    def test_expense_shifts_equity(self):
        Expense.objects.create(
            property=self.prop, paid_by=self.nick,
            amount=Decimal("10000"),
            date=datetime.date(2024, 2, 1),
            category="repair",
        )
        equity = calculate_equity(self.prop)
        self.assertGreater(equity[self.nick.id], equity[self.sarah.id])

	# check that if one owner performs labor, their equity increases
    def test_labor_shifts_equity(self):
        Labor.objects.create(
            property=self.prop, performed_by=self.sarah,
            hours=Decimal("10"), hourly_rate=Decimal("50"),
            date=datetime.date(2024, 2, 1),
        )
        equity = calculate_equity(self.prop)
        self.assertGreater(equity[self.sarah.id], equity[self.nick.id])