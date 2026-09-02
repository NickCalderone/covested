from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from properties.models import Property, PropertyOwnership

User = get_user_model()


class PropertyOwnershipSerializer(serializers.ModelSerializer):
	username = serializers.CharField(source="user.username", read_only=True)

	class Meta:
		model = PropertyOwnership
		fields = ["id", "user", "username", "initial_contribution", "joined_at"]


class PropertySerializer(serializers.ModelSerializer):
	owners = PropertyOwnershipSerializer(source="property_owners", many=True, read_only=True)

	class Meta:
		model = Property
		fields = ["id", "address", "purchase_price", "purchase_date", "estimated_value", "owners", "created_at"]


class PropertyCreateSerializer(PropertySerializer):
	# the creator becomes the first owner, so their stake is part of creating the property
	initial_contribution = serializers.DecimalField(max_digits=12, decimal_places=2, write_only=True)
	joined_at = serializers.DateField(write_only=True, required=False)

	class Meta(PropertySerializer.Meta):
		fields = PropertySerializer.Meta.fields + ["initial_contribution", "joined_at"]

	def create(self, validated_data):
		initial_contribution = validated_data.pop("initial_contribution")
		joined_at = validated_data.pop("joined_at", None)

		with transaction.atomic():
			prop = Property.objects.create(**validated_data)
			PropertyOwnership.objects.create(
				user=self.context["request"].user,
				property=prop,
				initial_contribution=initial_contribution,
				# the creator owned it from the day it was bought
				joined_at=joined_at or prop.purchase_date,
			)
		return prop


class AddOwnerSerializer(serializers.Serializer):
	username = serializers.CharField(write_only=True)
	initial_contribution = serializers.DecimalField(max_digits=12, decimal_places=2)
	joined_at = serializers.DateField(required=False)

	def validate(self, attrs):
		prop = self.context["property"]

		try:
			user = User.objects.get(username=attrs["username"])
		except User.DoesNotExist:
			raise serializers.ValidationError({"username": "No user with that username."})

		if PropertyOwnership.objects.filter(property=prop, user=user).exists():
			raise serializers.ValidationError({"username": "This user already owns this property."})

		attrs["user"] = user
		return attrs

	def create(self, validated_data):
		return PropertyOwnership.objects.create(
			user=validated_data["user"],
			property=self.context["property"],
			initial_contribution=validated_data["initial_contribution"],
			# a co-owner added now joined now, unless told otherwise
			joined_at=validated_data.get("joined_at") or timezone.now().date(),
		)
