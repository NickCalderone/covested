from decimal import Decimal
from django.db.models import Sum
from properties.models import PropertyOwnership
from expenses.models import Expense
from labor.models import Labor

class calculate_equity(property):
	# get owners
	ownerships = PropertyOwnership.objects.filter(property=property).select_related("user")

	# for each owner, calculate total contributions (initial + expenses + labor)
	contributions = {}

	for ownership in ownerships:
		user = ownership.user

	# calculate total property value (initial + expenses + labor)

	# calculate equity percentage for each owner based on their contributions vs total property value