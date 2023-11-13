from re import findall as re_findall
from uuid import uuid4
from os import makedirs as os_makedirs
from os.path import exists as os_path_exists

from django.db.models import (
    Model,
    ForeignKey,
    FileField,
    DateTimeField,
    UUIDField,
    CharField,
    CASCADE
)
from PyPDF2 import PdfReader
from cached_property import cached_property
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from django.conf import settings


def file_path(instance, filename):
    os_makedirs(settings.FILES_NAME, exist_ok=True)
    return 'files/' + uuid4().hex


class Case(Model):
    id = UUIDField(primary_key=True, default=uuid4, editable=False)
    user = ForeignKey(
        get_user_model(),
        on_delete=CASCADE,
        verbose_name='Пользователь'
    )
    debt_statement = FileField(
        upload_to=file_path,
        verbose_name='Расчеты по задолженности'
    )
    egrn = FileField(
        upload_to=file_path,
        blank=True,
        null=True,
        verbose_name='Выписка из ЕГРН'
    )
    
    created_at = DateTimeField(
        default=now,
        verbose_name='Дата создания'
    )

    TEMPLATE_CHOICES = (
        ('statement_magistrate', 'Приказ мировой суд'),
        ('lawsuit_district', 'Иск районный суд'),
        ('lawsuit_magistrate', 'Иск мировой суд'),
    )
    template = CharField(
        max_length=50,
        choices=TEMPLATE_CHOICES,
        default='statement_magistrate',
        verbose_name='Шаблон'
    )

    def __str__(self) -> bool:
        data = self.debt_statement_data
        def shorted_name(name: str) -> str:
            if not name:
                return
            surname, name, fathername, *_ = name.split()
            return f'{surname} {name[0]}. {fathername[0]}.'
        return ' '.join(
            field for field in (
                self.get_template_display(),
                shorted_name(data.get('name')),
                # data.get('period')
            )
            if field
        )

    class Meta:
        verbose_name = 'Дело'
        verbose_name_plural = 'Дела'

    def get_user_data(self) -> dict:
        user = self.user
        return {
            'org_name': user.label,
            'org_address': user.address,
            'org_representative_person': user.representative_person,
            'org_ogrn': user.ogrn,
            'org_inn': user.inn,
            'org_kpp': user.kpp
        }

    @cached_property
    def debt_statement_data(self) -> dict:
        if not self.debt_statement:
            raise ValueError('No dect_statement file')

        if not os_path_exists(self.debt_statement.path):
            return {}

        text = ''
        with open(self.debt_statement.path, "rb") as file:
            pdf_reader = PdfReader(file)
            text += pdf_reader.pages[0].extract_text()
            text += pdf_reader.pages[-1].extract_text()

        return {
            'period': re_findall(r'за\s(?:(.*))\n', text)[0],
            'org_inn': re_findall(r'ИНН\s(?:(.*))\n', text)[0],
            'address': re_findall(r'Адрес:\s(?:(.*))\n', text)[0],
            'name': re_findall(r'Ответственный.*:(.*)\n', text)[0],
            'date': re_findall(r'Долг\sна\s([0-9.]*)\s', text)[0],
            'amount': float(re_findall(r'составляет\s([0-9., ]*) руб.', text)[0].replace(' ', '').replace(',', '.'))
        }

    @cached_property
    def data(self) -> dict:
        data = self.get_user_data()
        data.update(self.debt_statement_data)
        data.update({'movements': list(self.get_template)})
        return data

    @cached_property
    def get_template(self):
        amount = self.amount

        if amount > 500000:
            return 'lawsuit_district', 'receipt_district'
        elif amount > 50000:
            return 'lawsuit_magistrate', 'receipt_magistrate'
        else:
            return 'statement_magistrate', 'receipt_magistrate'

    @cached_property
    def get_egrn_data(self) -> dict:
        return {}
    
    @cached_property
    def amount(self) -> float:
        return self.debt_statement_data['amount']
