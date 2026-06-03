from rest_framework import viewsets, permissions
from labor.models import Labor
from labor.serializers import LaborSerializer


class LaborViewSet(viewsets.ModelViewSet):
    serializer_class = LaborSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Labor.objects.filter(property__owners=self.request.user)

    def perform_create(self, serializer):
        serializer.save(performed_by=self.request.user)

