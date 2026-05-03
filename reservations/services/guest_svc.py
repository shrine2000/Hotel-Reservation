from reservations.exceptions import GuestProfileAlreadyExistsError
from reservations.models.guest import GuestProfile


def create_guest_profile(user, **kwargs) -> GuestProfile:
    if GuestProfile.objects.filter(user=user).exists():
        raise GuestProfileAlreadyExistsError()
    return GuestProfile.objects.create(user=user, **kwargs)


def update_guest_profile(profile: GuestProfile, **kwargs) -> GuestProfile:
    for field, value in kwargs.items():
        setattr(profile, field, value)
    profile.save(update_fields=list(kwargs.keys()))
    return profile
