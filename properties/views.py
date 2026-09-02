from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from properties.models import Property
from properties.serializers import (
    AddOwnerSerializer,
    PropertyCreateSerializer,
    PropertyOwnershipSerializer,
    PropertySerializer,
)
from properties.services import calculate_equity

class PropertyViewSet(viewsets.ModelViewSet):
    serializer_class = PropertySerializer
    permission_classes = [permissions.IsAuthenticated]

    # only allow users to see properties they own
    def get_queryset(self):
        return Property.objects.filter(owners=self.request.user)

    def get_serializer_class(self):
        if self.action == "create":
            return PropertyCreateSerializer
        return PropertySerializer

    @action(detail=True, methods=["post"], url_path="owners")
    def add_owner(self, request, pk=None):
        prop = self.get_object()
        serializer = AddOwnerSerializer(data=request.data, context={"property": prop})
        serializer.is_valid(raise_exception=True)
        ownership = serializer.save()
        return Response(PropertyOwnershipSerializer(ownership).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"])
    def equity(self, request, pk=None):
        prop = self.get_object()
        return Response(calculate_equity(prop))
