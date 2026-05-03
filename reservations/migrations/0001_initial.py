import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
import phonenumber_field.modelfields
import reservations.models.base_models
import reservations.validators
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        error_messages={
                            "unique": "A user with that username already exists."
                        },
                        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
                        max_length=150,
                        unique=True,
                        validators=[
                            django.contrib.auth.validators.UnicodeUsernameValidator()
                        ],
                        verbose_name="username",
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        blank=True, max_length=254, verbose_name="email address"
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, db_column="created_at"),
                ),
                (
                    "last_updated_at",
                    reservations.models.base_models.LastUpdatedDateField(
                        auto_now=True, db_column="last_updated_at"
                    ),
                ),
                (
                    "uid",
                    models.CharField(
                        db_index=True,
                        default=reservations.models.base_models.generate_uuid,
                        editable=False,
                        max_length=15,
                        unique=True,
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        blank=True,
                        max_length=150,
                        validators=[
                            reservations.validators.CharacterPatternValidator(
                                "PERSON_NAME"
                            )
                        ],
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True,
                        max_length=150,
                        validators=[
                            reservations.validators.CharacterPatternValidator(
                                "PERSON_NAME"
                            )
                        ],
                    ),
                ),
                (
                    "phone",
                    phonenumber_field.modelfields.PhoneNumberField(
                        blank=True, max_length=128, region=None
                    ),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "db_table": "users",
            },
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name="GuestProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, db_column="created_at"),
                ),
                (
                    "last_updated_at",
                    reservations.models.base_models.LastUpdatedDateField(
                        auto_now=True, db_column="last_updated_at"
                    ),
                ),
                (
                    "uid",
                    models.CharField(
                        db_index=True, editable=False, max_length=20, unique=True
                    ),
                ),
                (
                    "phone",
                    phonenumber_field.modelfields.PhoneNumberField(
                        blank=True, max_length=128, region=None
                    ),
                ),
                (
                    "address",
                    models.TextField(
                        blank=True,
                        validators=[
                            reservations.validators.CharacterPatternValidator("ADDRESS")
                        ],
                    ),
                ),
                (
                    "id_type",
                    models.CharField(
                        blank=True,
                        max_length=30,
                        validators=[
                            reservations.validators.CharacterPatternValidator(
                                "ALPHANUMERIC"
                            )
                        ],
                    ),
                ),
                (
                    "id_number",
                    models.CharField(
                        blank=True,
                        max_length=50,
                        validators=[
                            reservations.validators.CharacterPatternValidator(
                                "ALPHANUMERIC_WITH_DASH"
                            )
                        ],
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="guest_profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Hotel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, db_column="created_at"),
                ),
                (
                    "last_updated_at",
                    reservations.models.base_models.LastUpdatedDateField(
                        auto_now=True, db_column="last_updated_at"
                    ),
                ),
                (
                    "uid",
                    models.CharField(
                        db_index=True,
                        default=reservations.models.base_models.generate_uuid,
                        editable=False,
                        max_length=15,
                        unique=True,
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=100,
                        validators=[
                            django.core.validators.MinLengthValidator(2),
                            reservations.validators.CharacterPatternValidator(
                                "COMPANY_NAME"
                            ),
                        ],
                    ),
                ),
                (
                    "location",
                    models.CharField(
                        max_length=100,
                        validators=[
                            django.core.validators.MinLengthValidator(2),
                            reservations.validators.CharacterPatternValidator(
                                "ADDRESS"
                            ),
                        ],
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        validators=[
                            reservations.validators.CharacterPatternValidator(
                                "SAFE_TEXT"
                            )
                        ]
                    ),
                ),
                (
                    "star_rating",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (1, "1 Star"),
                            (2, "2 Stars"),
                            (3, "3 Stars"),
                            (4, "4 Stars"),
                            (5, "5 Stars"),
                        ],
                        default=3,
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                (
                    "admin",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="hotels",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="HotelPhoto",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, db_column="created_at"),
                ),
                (
                    "last_updated_at",
                    reservations.models.base_models.LastUpdatedDateField(
                        auto_now=True, db_column="last_updated_at"
                    ),
                ),
                (
                    "uid",
                    models.CharField(
                        db_index=True, editable=False, max_length=20, unique=True
                    ),
                ),
                ("url", models.URLField(max_length=500)),
                (
                    "caption",
                    models.CharField(
                        blank=True,
                        max_length=200,
                        validators=[
                            reservations.validators.validate_not_blank,
                            reservations.validators.CharacterPatternValidator(
                                "SAFE_TEXT"
                            ),
                        ],
                    ),
                ),
                ("is_primary", models.BooleanField(default=False)),
                (
                    "hotel",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="photos",
                        to="reservations.hotel",
                    ),
                ),
            ],
            options={
                "ordering": ["-is_primary", "created_at"],
            },
        ),
        migrations.CreateModel(
            name="Room",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, db_column="created_at"),
                ),
                (
                    "last_updated_at",
                    reservations.models.base_models.LastUpdatedDateField(
                        auto_now=True, db_column="last_updated_at"
                    ),
                ),
                (
                    "uid",
                    models.CharField(
                        db_index=True,
                        default=reservations.models.base_models.generate_uuid,
                        editable=False,
                        max_length=15,
                        unique=True,
                    ),
                ),
                (
                    "room_type",
                    models.CharField(
                        choices=[("S", "Single"), ("D", "Double"), ("SU", "Suite")],
                        max_length=2,
                    ),
                ),
                (
                    "luxury",
                    models.CharField(
                        choices=[("D", "Deluxe"), ("SD", "Super deluxe")], max_length=2
                    ),
                ),
                (
                    "base_cost",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=10,
                        validators=[
                            django.core.validators.MinValueValidator(Decimal("0.01"))
                        ],
                    ),
                ),
                ("available_rooms", models.PositiveIntegerField()),
                (
                    "max_guests",
                    models.PositiveSmallIntegerField(
                        default=2,
                        validators=[django.core.validators.MinValueValidator(1)],
                    ),
                ),
                ("amenities", models.JSONField(blank=True, default=list)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "hotel",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="rooms",
                        to="reservations.hotel",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Reservation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, db_column="created_at"),
                ),
                (
                    "last_updated_at",
                    reservations.models.base_models.LastUpdatedDateField(
                        auto_now=True, db_column="last_updated_at"
                    ),
                ),
                (
                    "uid",
                    models.CharField(
                        db_index=True,
                        default=reservations.models.base_models.generate_uuid,
                        editable=False,
                        max_length=15,
                        unique=True,
                    ),
                ),
                ("check_in_date", models.DateField(db_index=True)),
                (
                    "number_of_days",
                    models.PositiveIntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(365),
                        ]
                    ),
                ),
                (
                    "total_cost",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=10,
                        validators=[
                            django.core.validators.MinValueValidator(Decimal("0.01"))
                        ],
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("PE", "Pending"),
                            ("CO", "Confirmed"),
                            ("CI", "Checked in"),
                            ("CH", "Checked out"),
                            ("CA", "Cancelled"),
                        ],
                        db_index=True,
                        default="PE",
                        max_length=2,
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reservations",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "room",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reservations",
                        to="reservations.room",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="HotelReview",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, db_column="created_at"),
                ),
                (
                    "last_updated_at",
                    reservations.models.base_models.LastUpdatedDateField(
                        auto_now=True, db_column="last_updated_at"
                    ),
                ),
                (
                    "uid",
                    models.CharField(
                        db_index=True, editable=False, max_length=20, unique=True
                    ),
                ),
                (
                    "rating",
                    models.PositiveSmallIntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(5),
                        ]
                    ),
                ),
                (
                    "comment",
                    models.TextField(
                        blank=True,
                        validators=[
                            reservations.validators.CharacterPatternValidator(
                                "SAFE_TEXT"
                            )
                        ],
                    ),
                ),
                (
                    "hotel",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reviews",
                        to="reservations.hotel",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reviews",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "unique_together": {("hotel", "user")},
            },
        ),
        migrations.CreateModel(
            name="Payment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, db_column="created_at"),
                ),
                (
                    "last_updated_at",
                    reservations.models.base_models.LastUpdatedDateField(
                        auto_now=True, db_column="last_updated_at"
                    ),
                ),
                (
                    "uid",
                    models.CharField(
                        db_index=True, editable=False, max_length=20, unique=True
                    ),
                ),
                (
                    "amount",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=10,
                        validators=[
                            django.core.validators.MinValueValidator(Decimal("0.01"))
                        ],
                    ),
                ),
                (
                    "payment_method",
                    models.CharField(
                        choices=[
                            ("CA", "Cash"),
                            ("CC", "Credit card"),
                            ("ON", "Online"),
                        ],
                        max_length=2,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("PE", "Pending"),
                            ("CO", "Completed"),
                            ("FA", "Failed"),
                            ("RE", "Refunded"),
                        ],
                        db_index=True,
                        default="PE",
                        max_length=2,
                    ),
                ),
                (
                    "reference_id",
                    models.CharField(
                        blank=True,
                        max_length=100,
                        validators=[
                            reservations.validators.CharacterPatternValidator(
                                "REFERENCE_ID"
                            )
                        ],
                    ),
                ),
                (
                    "notes",
                    models.TextField(
                        blank=True,
                        validators=[
                            reservations.validators.CharacterPatternValidator(
                                "SAFE_TEXT"
                            )
                        ],
                    ),
                ),
                (
                    "reservation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="payments",
                        to="reservations.reservation",
                    ),
                ),
            ],
            options={
                "indexes": [
                    models.Index(
                        fields=["reservation", "status"],
                        name="reservation_reserva_95f990_idx",
                    )
                ],
            },
        ),
        migrations.AddIndex(
            model_name="reservation",
            index=models.Index(
                fields=["user", "status"], name="reservation_user_id_b23f11_idx"
            ),
        ),
    ]
