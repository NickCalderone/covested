from rest_framework import viewsets, permissions
from expenses.models import Expense
from expenses.serializers import ExpenseSerializer


class ExpenseViewSet(viewsets.ModelViewSet):
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Expense.objects.filter(property__owners=self.request.user)

    def perform_create(self, serializer):
        serializer.save(paid_by=self.request.user)

