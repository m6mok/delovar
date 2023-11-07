from functools import cached_property
from re import findall as re_findall
from functools import wraps
from uuid import uuid4
from os import makedirs as os_makedirs
from os.path import exists as os_path_exists

from django.db.models import (
    Model,
    ForeignKey,
    FileField,
    DateTimeField,
    UUIDField,
    CASCADE
)
from django.utils.timezone import now
from PyPDF2 import PdfReader
from requests.exceptions import ConnectionError as RequestsConnectionError
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from requests import get as requests_get, post as requests_post
from django.db.models.signals import post_save
from django.conf import settings


def file_path(instance, filename):
    os_makedirs(settings.FILES_NAME, exist_ok=True)
    return settings.FILES_NAME / uuid4().hex


class Session:
    def __init__(self, is_active: bool, id: int = None):
        self.is_active = is_active
        self.id = id

    def __str__(self) -> str:
        return f'Сессия({self.number})'

    def check(self) -> bool:
        response = requests_get(
            settings.API_URL_CHECK,
            json={'session_id': self.id},
            headers={'x-access-token': settings.API_ACCESS_TOKEN}
        )
        data = response.json()
        
        return data['result']


class Case(Model):
    id = UUIDField(primary_key=True, default=uuid4, editable=False)
    user = ForeignKey(
        get_user_model(),
        on_delete=CASCADE,
        verbose_name='Пользователь'
    )
    receipt = FileField(
        upload_to=file_path,
        blank=True,
        null=True,
        verbose_name='Квитанция об уплате госпошлины'
    )
    statement = FileField(
        upload_to=file_path,
        blank=True,
        null=True,
        verbose_name='Заявление'
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

    def __str__(self) -> bool:
        data = self.debt_statement_data
        def shorted_name(name: str) -> str:
            if not name:
                return
            surname, name, fathername, *_ = name.split()
            return f'{surname} {name[0]}. {fathername[0]}.'
        return ' '.join(
            field for field in (shorted_name(data.get('name')), data.get('period'))
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
            'period': re_findall('за\s(?:(.*))\n', text)[0],
            'org_inn': re_findall('ИНН\s(?:(.*))\n', text)[0],
            'address': re_findall('Адрес:\s(?:(.*))\n', text)[0],
            'name': re_findall('Ответственный.*:(.*)\n', text)[0],
            'date': re_findall('Долг\sна\s([0-9.]*)\s', text)[0],
            'amount': float(re_findall('составляет\s([0-9., ]*) руб.', text)[0].replace(' ', '').replace(',', '.'))
        }


def api():
    def decorator(func):
        @wraps(func)
        def wrapper(case):
            _settings, data = func(case)

            json_data = {
                'settings': _settings,
                'data': data
            }

            try:
                response = requests_post(
                    settings.API_URL_DOCUMENT,
                    json=json_data,
                    headers={
                        'x-access-token': settings.API_ACCESS_TOKEN
                    }
                )
                if response.status_code == 200:
                    ...
            except RequestsConnectionError as rce:
                print(f'''
                    [Error] Failed to fetch data.
                    : {rce}
                ''')
        return wrapper
    return decorator

@receiver(post_save, sender=Case)
def create_case_files(sender, instance, **kwargs):
    if not instance.debt_statement:
        return

    if not instance.receipt:
        receipt(instance)
    if not instance.statement:
        statement(instance)


@api()
def receipt(case: Case):
    data = case.get_user_data()
    data.update(case.debt_statement_data)

    _settings: dict = settings.API_DEFAULT_SETTINGS
    _settings.update(settings.API_MOVEMENT_RECEIPT)
    _settings.update({'case_id': str(case.id)})
    
    return _settings, data


@api()
def statement(case: Case):
    data = case.get_user_data()
    data.update(case.debt_statement_data)
    if case.egrn:
        data.update(get_egrn_data(case.egrn.path))

    amount = data.get('amount')
    if not amount or not isinstance(amount, float):
        raise ValueError('No amount in data')

    org_inn = data.get('org_inn')
    if org_inn != data['org_inn']:
        raise ValueError('Wrong org_inn in data')

    _settings: dict = settings.API_DEFAULT_SETTINGS
    if data['amount'] > 500000:
        _settings.update(settings.API_MOVEMENT_LOWSUIT)
    elif data['amount'] > 50000:
        _settings.update(settings.API_MOVEMENT_STATEMENT_DISTRICT)
    else:
        _settings.update(settings.API_MOVEMENT_STATEMENT_MAGISTRATE)
    _settings.update({'case_id': str(case.id)})


    return _settings, data


def get_egrn_data(egrn_path: str) -> dict:
    return {}
