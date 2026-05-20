import uuid
from django.db import models
from django.conf import settings

class Labor(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	property = models.ForeignKey("properties.Property", on_delete=models.PROTECT, related_name="labor")
	performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="labor_performed")
	hours = models.DecimalField(max_digits=6, decimal_places=2)
	hourly_rate = models.DecimalField(max_digits=8, decimal_places=2)
	date = models.DateField()
	description = models.CharField(max_length=255, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta: 
		ordering = ["-date", "-created_at"]

	def __str__(self):
		return f"{self.performed_by} worked {self.hours} hours at {self.hourly_rate} for {self.property} on {self.date}"