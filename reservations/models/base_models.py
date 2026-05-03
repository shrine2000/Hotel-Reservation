import sys
import uuid

from django.db import IntegrityError, models, transaction


def _is_api_context() -> bool:
    return "migrate" not in sys.argv and "shell_plus" not in sys.argv


class LastUpdatedDateField(models.DateTimeField):
    def __init__(self, *args, **kwargs):
        if _is_api_context():
            kwargs["auto_now"] = True
        else:
            kwargs["auto_now_add"] = True
        super().__init__(*args, **kwargs)


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_column="created_at")
    last_updated_at = LastUpdatedDateField(db_column="last_updated_at")

    class Meta:
        abstract = True

    def save(self, **kwargs):
        update_fields = kwargs.get("update_fields", None)
        if update_fields and "last_updated_at" not in update_fields:
            kwargs["update_fields"] = list(update_fields) + ["last_updated_at"]
        super().save(**kwargs)


def generate_uuid(length: int = 10) -> int:
    while True:
        uid = int(uuid.uuid4().int >> 64) % 10**length
        if len(str(uid)) == length:
            return uid


class UUIDModel(models.Model):
    MAX_UID_RETRIES = 5
    uid = models.CharField(
        default=generate_uuid, unique=True, editable=False, db_index=True, max_length=15
    )

    class Meta:
        abstract = True

    def save(self, **kwargs):
        if self.pk:
            return super().save(**kwargs)

        for attempt in range(self.MAX_UID_RETRIES):
            if attempt > 0:
                self.uid = generate_uuid()
            try:
                with transaction.atomic():
                    return super().save(**kwargs)
            except IntegrityError as exc:
                if "uid" not in str(exc).lower():
                    raise
                if attempt >= self.MAX_UID_RETRIES - 1:
                    raise RuntimeError(
                        f"Failed to generate a unique UID for {self.__class__.__name__} "
                        f"after {self.MAX_UID_RETRIES} attempts."
                    ) from exc
        return None


class CustomIDModel(models.Model):
    id_prefix: str = ""
    id_length: int = 10
    MAX_UID_RETRIES = 5
    uid = models.CharField(unique=True, editable=False, db_index=True, max_length=20)

    class Meta:
        abstract = True

    def save(self, **kwargs):
        if self.pk:
            return super().save(**kwargs)

        if not self.id_prefix:
            raise ValueError(f"{self.__class__.__name__} must define 'id_prefix'")

        for attempt in range(self.MAX_UID_RETRIES):
            self.uid = f"{self.id_prefix}{generate_uuid(self.id_length)}"
            try:
                with transaction.atomic():
                    super().save(**kwargs)
                return
            except IntegrityError as exc:
                if "uid" not in str(exc).lower():
                    raise
                if attempt >= self.MAX_UID_RETRIES - 1:
                    raise RuntimeError(
                        f"Failed to generate a unique UID for {self.__class__.__name__} "
                        f"after {self.MAX_UID_RETRIES} attempts."
                    ) from exc


class FullNameMixin(models.Model):
    class Meta:
        abstract = True

    @property
    def full_name(self) -> str:
        title = getattr(self, "title", None)
        first = (getattr(self, "first_name", "") or "").strip()
        last = (getattr(self, "last_name", "") or "").strip()
        parts = []
        if title:
            parts.append(str(title).strip())
        name = f"{first} {last}".strip()
        if name:
            parts.append(name)
        return " ".join(parts).strip()

    def get_full_name(self) -> str:
        return self.full_name
