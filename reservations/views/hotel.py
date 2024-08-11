from rest_framework import generics, permissions, status
from rest_framework.response import Response
from reservations.models.hotel import Hotel
from reservations.serializers import HotelSerializer


class HotelListView(generics.ListAPIView):
    queryset = Hotel.objects.filter(is_active=True)
    serializer_class = HotelSerializer
    permission_classes = [permissions.IsAuthenticated]


class HotelDetailView(generics.RetrieveAPIView):
    queryset = Hotel.objects.filter(is_active=True)
    serializer_class = HotelSerializer
    permission_classes = [permissions.IsAuthenticated]


class HotelCreateView(generics.CreateAPIView):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    permission_classes = [permissions.IsAdminUser]


class HotelUpdateView(generics.UpdateAPIView):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    permission_classes = [permissions.IsAdminUser]


class HotelDeactivateView(generics.UpdateAPIView):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    permission_classes = [permissions.IsAdminUser]

    def patch(self, request, *args, **kwargs):
        hotel = self.get_object()
        hotel.is_active = False
        hotel.save()
        return Response({"status": "Hotel deactivated"}, status=status.HTTP_200_OK)
