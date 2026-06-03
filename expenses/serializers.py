from rest_framework import serializers
from expenses.models import Expense


class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = ["id", "property", "paid_by", "amount", "date", "category", "description", "created_at"]
        read_only_fields = ["paid_by", "created_at"]
