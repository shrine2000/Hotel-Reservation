import logging
from typing import Any

from django_filters.rest_framework import DjangoFilterBackend
from dry_rest_permissions.generics import DRYPermissions
from rest_framework import viewsets, status, filters
from rest_framework.request import Request
from rest_framework.response import Response

from reservations.filters import HotelReviewFilter
from reservations.models.review import HotelReview
from reservations.serializers.review_serializers import (
    HotelReviewCreateSerializer,
    HotelReviewSerializer,
    HotelReviewUpdateSerializer,
)
from reservations.services import review_svc

logger = logging.getLogger(__name__)


class HotelReviewViewSet(viewsets.ModelViewSet):
    permission_classes = (DRYPermissions,)
    lookup_field = "uid"
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = HotelReviewFilter
    ordering_fields = ["rating", "created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return (
            HotelReview.objects.using("replica")
            .select_related("user", "hotel")
            .only(
                "uid",
                "rating",
                "comment",
                "created_at",
                "last_updated_at",
                "user__username",
                "hotel__uid",
                "user_id",
                "hotel_id",
            )
            .order_by("-created_at")
        )

    def get_serializer_class(self):
        if self.action == "create":
            return HotelReviewCreateSerializer
        if self.action in ("update", "partial_update"):
            return HotelReviewUpdateSerializer
        return HotelReviewSerializer

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = HotelReviewCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        review = review_svc.create_review(
            user=request.user,
            hotel=serializer.validated_data["hotel_uid"],
            rating=serializer.validated_data["rating"],
            comment=serializer.validated_data.get("comment", ""),
        )
        return Response(
            HotelReviewSerializer(review).data, status=status.HTTP_201_CREATED
        )

    def partial_update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        review = self.get_object()
        serializer = HotelReviewUpdateSerializer(
            review, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        updated = review_svc.create_review(
            user=review.user,
            hotel=review.hotel,
            rating=serializer.validated_data.get("rating", review.rating),
            comment=serializer.validated_data.get("comment", review.comment),
        )
        return Response(HotelReviewSerializer(updated).data)

    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        review = self.get_object()
        review_svc.delete_review(review)
        return Response(status=status.HTTP_204_NO_CONTENT)
