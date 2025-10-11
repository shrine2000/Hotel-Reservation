from rest_framework import generics, status
from rest_framework.response import Response
from dry_rest_permissions.generics import DRYPermissions
from reservations.models.hotel import Hotel
from reservations.serializers import HotelSerializer


class HotelListView(generics.ListAPIView):
    queryset = Hotel.objects.filter(is_active=True)
    serializer_class = HotelSerializer
    permission_classes = (DRYPermissions,)


class HotelDetailView(generics.RetrieveAPIView):
    queryset = Hotel.objects.filter(is_active=True)
    serializer_class = HotelSerializer
    permission_classes = (DRYPermissions,)


class HotelCreateView(generics.CreateAPIView):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    permission_classes = (DRYPermissions,)


class HotelUpdateView(generics.UpdateAPIView):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    permission_classes = (DRYPermissions,)


class HotelDeactivateView(generics.UpdateAPIView):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    permission_classes = (DRYPermissions,)

    def patch(self, request, *args, **kwargs):
        hotel = self.get_object()
        hotel.is_active = False
        hotel.save()
        return Response({"status": "Hotel deactivated"}, status=status.HTTP_200_OK)
