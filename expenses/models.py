import uuid
from django.db import models
from django.conf import settings

# Create your models here.
class Expense(models.Model):
	class Category(models.TextChoices):
		MORTGAGE = "mortgage", "Mortgage"
		TAX = "tax", "Property Tax"
		INSURANCE = "insurance", "Insurance"
		REPAIRS = "repairs", "Repairs & Maintenance"
		IMPROVEMENT = "improvement", "Improvement"
		UTILITIES = "utilities", "Utilities"
		OTHER = "other", "Other"

	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	# properties.Property = [app][model] to avoid circular import issues
	property = models.ForeignKey("properties.Property", on_delete=models.PROTECT, related_name="expenses")
	paid_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="paid_expenses")
	amount = models.DecimalField(max_digits=12, decimal_places=2)
	date = models.DateField()
	category = models.CharField(max_length=50, choices=Category.choices)
	description = models.CharField(max_length=255, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["-date", "-created_at"]

	def __str__(self):
		return f"{self.paid_by} paid {self.amount} for {self.get_category_display()} on {self.date}"