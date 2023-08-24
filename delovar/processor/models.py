from django.db import models
import os

from user.models import CustomUser


def get_upload_path(instance, filename):
    folder_name = f"case_{instance.case.id}"
    return os.path.join("documents", folder_name, filename)


class Case(models.Model):
    name = models.CharField(
        verbose_name='Имя подсудимого',
        max_length=200
    )
    address = models.CharField(
        verbose_name='Адрес подсудимого',
        max_length=200
    )
    period = models.CharField(
        verbose_name='Период задолжности',
        max_length=100
    )
    payment_amount = models.DecimalField(
        verbose_name='Сумма задолжности',
        max_digits=10,
        decimal_places=2
    )
    owner = models.ForeignKey(
        CustomUser,
        verbose_name='Оформитель',
        on_delete=models.CASCADE
    )

    FORMAT_CHOICES = (
        ("Заполнение", "Заполнение"),
        ("Суд", "Суд"),
        ("Иск", "Иск"),
    )
    format = models.CharField(
        verbose_name='Формат заявления',
        max_length=20,
        choices=FORMAT_CHOICES
    )

    def __str__(self):
        return f'{self.name}, {self.period}'


class Document(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE)
    document_file = models.FileField(upload_to=get_upload_path)
    
    def __str__(self):
        return f"Document for {self.case.name}"
