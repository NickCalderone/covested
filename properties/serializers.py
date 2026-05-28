from rest_framework import serializers
from properties.models import Property, PropertyOwnership

class PropertyOwnershipSerializer(serializers.ModelSerializer):
	class Meta:
		model = PropertyOwnership
		fields = ["id", "user", "initial_contribution", "joined_at"]

class PropertySerializer(serializers.ModelSerializer):
	owners = PropertyOwnershipSerializer(source="property_owners", many=True, read_only=True)

	class Meta:
		model = Property
		fields = ["id", "address", "purchase_price", "purchase_date", "estimated_value", "owners", "created_at"]