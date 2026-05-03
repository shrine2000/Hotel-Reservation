from reservations.models.hotel import Hotel
from reservations.models.review import HotelReview


def create_review(user, hotel: Hotel, rating: int, comment: str = "") -> HotelReview:
    review, created = HotelReview.objects.get_or_create(
        user=user,
        hotel=hotel,
        defaults={"rating": rating, "comment": comment},
    )
    if not created:
        review.rating = rating
        review.comment = comment
        review.save(update_fields=["rating", "comment"])
    return review


def delete_review(review: HotelReview) -> None:
    review.delete()
