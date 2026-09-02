# calculate equity percentage for each owner based on their contributions vs total property value
from decimal import Decimal
from django.test import TestCase
from rest_framework.test import APITestCase
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

class PropertyOwnershipApiTests(APITestCase):

    def setUp(self):
        self.nick = User.objects.create_user(username="nick", password="pass")
        self.sarah = User.objects.create_user(username="sarah", password="pass")
        self.client.force_authenticate(user=self.nick)

        self.payload = {
            "address": "123 Main St",
            "purchase_price": "400000.00",
            "purchase_date": "2024-01-01",
            "initial_contribution": "200000.00",
        }

    def create_property(self):
        return self.client.post("/api/properties/", self.payload, format="json")

    # creating a property should make the creator an owner, so they can still see it
    def test_create_property_makes_creator_an_owner(self):
        response = self.create_property()
        self.assertEqual(response.status_code, 201)

        prop = Property.objects.get(id=response.data["id"])
        ownership = PropertyOwnership.objects.get(property=prop, user=self.nick)
        self.assertEqual(ownership.initial_contribution, Decimal("200000.00"))

        listed = self.client.get("/api/properties/")
        self.assertEqual([p["id"] for p in listed.data], [str(prop.id)])

    # without an explicit joined_at, the creator owned it from the purchase date
    def test_joined_at_defaults_to_purchase_date(self):
        self.create_property()
        ownership = PropertyOwnership.objects.get(user=self.nick)
        self.assertEqual(ownership.joined_at, datetime.date(2024, 1, 1))

    def test_initial_contribution_is_required(self):
        del self.payload["initial_contribution"]
        response = self.create_property()
        self.assertEqual(response.status_code, 400)
        self.assertIn("initial_contribution", response.data)
        self.assertFalse(Property.objects.exists())

    # a co-owner added through the API can see the property and counts toward equity
    def test_add_co_owner(self):
        prop_id = self.create_property().data["id"]
        response = self.client.post(
            f"/api/properties/{prop_id}/owners/",
            {"username": "sarah", "initial_contribution": "200000.00"},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["username"], "sarah")

        self.client.force_authenticate(user=self.sarah)
        listed = self.client.get("/api/properties/")
        self.assertEqual([p["id"] for p in listed.data], [prop_id])

        equity = self.client.get(f"/api/properties/{prop_id}/equity/")
        self.assertEqual(equity.data[self.sarah.id], Decimal("50.0000"))

    def test_add_owner_rejects_unknown_username(self):
        prop_id = self.create_property().data["id"]
        response = self.client.post(
            f"/api/properties/{prop_id}/owners/",
            {"username": "nobody", "initial_contribution": "100.00"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("username", response.data)

    def test_add_owner_rejects_duplicate(self):
        prop_id = self.create_property().data["id"]
        response = self.client.post(
            f"/api/properties/{prop_id}/owners/",
            {"username": "nick", "initial_contribution": "100.00"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(PropertyOwnership.objects.filter(user=self.nick).count(), 1)

    # a stranger must not be able to add themselves to someone else's property
    def test_non_owner_cannot_add_owner(self):
        prop_id = self.create_property().data["id"]
        self.client.force_authenticate(user=self.sarah)
        response = self.client.post(
            f"/api/properties/{prop_id}/owners/",
            {"username": "sarah", "initial_contribution": "1.00"},
            format="json",
        )
        self.assertEqual(response.status_code, 404)
        self.assertFalse(PropertyOwnership.objects.filter(user=self.sarah).exists())
