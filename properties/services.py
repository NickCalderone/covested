from decimal import Decimal
from django.db.models import Sum, F
from properties.models import PropertyOwnership
from expenses.models import Expense
from labor.models import Labor

def calculate_equity(prop):
	# get owners
	ownerships = PropertyOwnership.objects.filter(property=prop).select_related("user")

	# for each owner, calculate total contributions (initial + expenses + labor)
	contributions = {}

	for ownership in ownerships:
		user = ownership.user

		expenses_total = Expense.objects.filter(
			property=prop,
			paid_by=user
		).aggregate(
			total=Sum("amount")
		)["total"] or Decimal(0)

		labor_total = Labor.objects.filter(
			property=prop,
			performed_by=user
		).aggregate(
			total=Sum(F("hours") * F("hourly_rate"))
		)["total"] or Decimal(0)

		contributions[user.id] = (
			ownership.initial_contribution + expenses_total + labor_total
		)
	
	total = sum(contributions.values()) or Decimal(1)  # prevent division by zero

	return {
		user_id: round((amount / total) * 100, 4)
		for user_id, amount in contributions.items()
	}