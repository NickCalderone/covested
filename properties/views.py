from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from properties.models import Property
from properties.serializers import PropertySerializer
from properties.services import calculate_equity

class PropertyViewSet(viewsets.ModelViewSet):
    serializer_class = PropertySerializer
    permission_classes = [permissions.IsAuthenticated]

	# only allow users to see properties they own
    def get_queryset(self):
        return Property.objects.filter(owners=self.request.user)

    @action(detail=True, methods=["get"])
    def equity(self, request, pk=None):
        prop = self.get_object()
        return Response(calculate_equity(prop))