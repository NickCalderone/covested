import uuid
from django.db import models
from django.conf import settings


class Property(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    address = models.CharField(max_length=255)
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2)
    purchase_date = models.DateField()
    estimated_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    owners = models.ManyToManyField(settings.AUTH_USER_MODEL, through="PropertyOwner", related_name="properties")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address


# Intermediate model to represent ownership of a property by a user, along with their initial contribution and join date.
class PropertyOwner(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="property_ownerships")
    property = models.ForeignKey(Property, on_delete=models.PROTECT, related_name="property_owners")
    initial_contribution = models.DecimalField(max_digits=12, decimal_places=2)
    joined_at = models.DateField()

    class Meta:
        unique_together = ("user", "property")

    def __str__(self):
        return f"{self.user} → {self.property}"
