from uuid import uuid4
from os import makedirs as os_makedirs

from django.db import models
from django.core.validators import (
    MinLengthValidator,
    MaxLengthValidator
)
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
from django.conf import settings


def file_path(instance, filename):
    os_makedirs(settings.FILES_NAME, exist_ok=True)
    return 'files/' + uuid4().hex


class CustomUserManager(BaseUserManager):
    def create_user(
        self,
        inn,
        password,
        **extra_fields
    ):
        user = self.model(inn=inn, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        inn,
        password,
        **extra_fields
    ):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(
            inn,
            password,
            **extra_fields
        )


class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    inn = models.CharField(
        verbose_name='ИНН',
        max_length=12,
        unique=True,
        validators=[
            MinLengthValidator(10),
            MaxLengthValidator(12)
        ]
    )
    ogrn = models.CharField(
        verbose_name='ОГРН',
        max_length=15,
        unique=True,
        validators=[
            MinLengthValidator(13),
            MaxLengthValidator(15)
        ],
        blank=True,
        null=True,
    )
    kpp = models.CharField(
        verbose_name='КПП',
        max_length=9,
        unique=True,
        validators=[
            MinLengthValidator(9),
            MaxLengthValidator(9)
        ],
        blank=True,
        null=True,
    )

    label = models.CharField(
        verbose_name='Название организации',
        max_length=255,
        blank=True,
        null=True,
    )

    address = models.CharField(
        verbose_name='Адрес',
        max_length=255,
        blank=True,
        null=True,
    )

    representative_person = models.CharField(
        verbose_name='Представитель',
        max_length=255,
        blank=True,
        null=True,
    )

    mkd = models.FileField(
        upload_to=file_path,
        blank=True,
        null=True,
        verbose_name='Договор управления МКД'
    )

    egrul = models.FileField(
        upload_to=file_path,
        blank=True,
        null=True,
        verbose_name='Выписка из ЕГРЮЛ'
    )

    is_active = models.BooleanField(
        verbose_name='Активен',
        default=True
    )

    is_staff = models.BooleanField(
        verbose_name='Администратор',
        default=False
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'inn'
    REQUIRED_FIELDS = [
        'label',
        'address',
        'representative_person',
        'ogrn',
        'kpp',
        'mkd',
        'egrul'
    ]

    @property
    def is_authenticated(self):
        return self.is_active

    def __str__(self):
        return ', '.join(field for field in (
            self.label,
        ) if field)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
