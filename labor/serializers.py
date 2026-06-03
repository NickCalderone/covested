from rest_framework import serializers
from labor.models import Labor


class LaborSerializer(serializers.ModelSerializer):
    class Meta:
        model = Labor
        fields = ["id", "property", "performed_by", "hours", "hourly_rate", "date", "description", "created_at"]
        read_only_fields = ["performed_by", "created_at"]
