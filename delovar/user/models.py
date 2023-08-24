from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class CustomUserManager(BaseUserManager):
    def create_user(self, inn, password, email, address, leader_name, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(
            inn=inn,
            email=email,
            address=address,
            leader_name=leader_name,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, inn, password, email, address, leader_name, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(inn, password, email, address, leader_name, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    inn = models.CharField(
        verbose_name='ИНН',
        max_length=12,
        unique=True
    )
    email = models.EmailField(
        verbose_name='Email',
        unique=True
    )
    label = models.CharField(
        verbose_name='Организация',
        max_length=255
    )
    address = models.CharField(
        verbose_name='Адрес',
        max_length=255
    )
    leader_name = models.CharField(
        verbose_name='Представитель',
        max_length=255
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
        'email',
        'label',
        'address',
        'leader_name'
    ]

    @property
    def is_authenticated(self):
        return self.is_active

    def __str__(self):
        return f'{self.inn}, {self.label}'
    git config --global user.email "you@example.com"
  git config --global user.name "Your Name"
