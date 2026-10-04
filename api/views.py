from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .serializers import MonitorSerializer, CheckResultSerializer, RegistrationSerializer
from .models import Monitor


# My viewsets
class MonitorViewSet(viewsets.ModelViewSet):
    serializer_class = MonitorSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Monitor.objects.filter(owner=self.request.user).order_by("-created_at")

    @action(detail=True, methods=['get'], serializer_class=CheckResultSerializer)
    def results(self, request, pk=None):
        monitor = self.get_object()

        result_qsets = monitor.results.all()
        page = self.paginate_queryset(result_qsets)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(result_qsets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RegistrationView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]
