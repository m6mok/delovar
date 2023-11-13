from typing import List
from zipfile import ZipFile
from io import BytesIO
from os.path import exists as os_path_exists
from os import remove as os_remove
import logging
from re import findall as re_findall

from django.views.generic.edit import FormView
from django.views.generic import TemplateView
from django.core.files.base import ContentFile
from django.http import JsonResponse, HttpResponse
from requests.exceptions import ConnectionError as RequestsConnectionError
from requests import get as requests_get, post as requests_post
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.dispatch import receiver
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login # не трогать
from transliterate import slugify
from django.urls import reverse_lazy
from django.conf import settings
from django.db.models.signals import post_save
from PyPDF2 import PdfReader

from user.forms import CustomAuthenticationForm, CustomUserDocumentsForm
from .models import Case
from .forms import NewCaseForm, CaseDetailForm


def about(request):
    context = {}
    return render(request, 'main/about.html', context)


def prices(request):
    context = {}
    return render(request, 'main/prices.html', context)


def faq(request):
    context = {}
    return render(request, 'main/faq.html', context)


@method_decorator(login_required, name='dispatch')
class ProfileView(TemplateView):
    template_name = 'main/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_cases = Case.objects.filter(
            user=self.request.user
        ).order_by('-created_at')[:3]
        context['cases'] = user_cases
        return context


@login_required
def profile(request):
    user = request.user
    cases = Case.objects.filter(user=user).order_by('-created_at')

    if request.method == 'POST':
        form = CustomUserDocumentsForm(
            request.POST,
            request.FILES,
            instance=user
        )
        if form.is_valid():
            user = form.save()
    else:
        form = CustomUserDocumentsForm(instance=user)


    return render(request, 'main/profile.html', {
        'cases': cases,
        'user': user,
        'form': form
    })


@login_required
def case_detail(request, pk: str):
    case = get_object_or_404(Case, pk=pk, user=request.user)

    if request.method == 'POST':
        form = CaseDetailForm(request.POST, request.FILES, instance=case)
        if form.is_valid():
            case = form.save()
    else:
        form = CaseDetailForm(instance=case)

    context = {
        'case': case,
        'form': form,
        'statement': api_ready(
            str(case.user.id),
            str(case.id),
            case.get_template[0]
        )['result'],
        'receipt': api_ready(
            str(case.user.id),
            str(case.id),
            case.get_template[1]
        )['result']
    }

    return render(request, 'main/case.html', context)


@login_required
def new_case(request):
    if request.method == 'POST':
        form = NewCaseForm(request.POST, request.FILES)
        if form.is_valid():
            case: Case = form.save(commit=False)
            case.user = request.user
            case.save()
            case.template = case.get_template[0]
            case.save()
            return redirect('main:profile')
    else:
        form = NewCaseForm()

    return render(request, 'main/new_case.html', {'form': form})


class IndexView(FormView):
    template_name = 'main/index.html'
    form_class = CustomAuthenticationForm
    success_url = reverse_lazy('main:profile')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


@login_required
def check_receipt(request, pk: str):
    case = get_object_or_404(Case, pk=pk, user=request.user)
    return JsonResponse({
        'success': api_ready(
            str(case.user.id),
            str(case.id),
            case.get_template[1]
        )['message']
    })


@login_required
def check_statement(request, pk: str):
    case = get_object_or_404(Case, pk=pk, user=request.user)
    return JsonResponse({
        'success': api_ready(
            str(case.user.id),
            str(case.id),
            case.get_template[0]
        )['message']
    })


@login_required
def check_upload(request, pk: str):
    return JsonResponse({'success': upload_ready(pk, request.user)})


@login_required
def refresh_request(request, pk: str):
    case = get_object_or_404(Case, pk=pk)
    data = case.data
    api_upload(
        user_id=str(case.user.id),
        case_id=str(case.id),
        movements_list=data['movements'],
        plaintiff={
            'name': data['org_name'],
            'inn': data['org_inn'],
            'ogrn': data['org_ogrn'],
            'kpp': data['org_kpp'],
            'address': data['org_address'],
            'representative': data['org_representative_person']
        },
        defendant={
            'address': data['address'],
            'representative': data['name'],
        },
        arrears=data['amount'],
        date=data['date'],
        period=data['period'],
    )
    return JsonResponse({'success': upload_ready(pk, request.user)})


def upload_ready(pk: str, user) -> bool:
    case = get_object_or_404(Case, pk=pk, user=user)
    templates = [api_ready(str(case.user.id), str(case.id), template) for template in case.get_template]
    message = ''
    result = (
        bool(case.debt_statement) and
        bool(case.egrn) and
        bool(case.user.mkd) and
        bool(case.user.egrul) and
        all(template['result'] for template in templates)
    )
    if all(template['message'] == 'ready' for template in templates) and result:
        message = 'ready'
    elif all(template['message'] == 'failed' for template in templates):
        message = 'failed'
    elif all(template['message'] == 'wait' for template in templates):
        message = 'wait'
    elif all(template['message'] == 'lost_connection' for template in templates):
        message = 'lost_connection'
    logging.info(templates)
    return {
        'result': result,
        'message': message,
        'templates': templates
    }


@login_required
def create_document_pack(request, pk: str):
    case = get_object_or_404(Case, pk=pk, user=request.user)

    if not upload_ready(pk, request.user)['result']:
        return JsonResponse({'message': 'Some files are not ready'})

    # try:
    zip_buffer = BytesIO()

    with ZipFile(zip_buffer, 'w') as zip_file:
        zip_file.write(case.debt_statement.path, 'Расчеты по задолженности.pdf')
        zip_file.write(case.egrn.path, 'Выписка из ЕГРН.pdf')
        zip_file.write(case.user.mkd.path, 'Договор управления МКД.pdf')
        zip_file.write(case.user.egrul.path, 'Выписка из ЕГРЮЛ.pdf')
        zip_file.writestr(
            'Квитанция об уплате госпошлины.pdf',
            api_download(str(case.user.id), str(case.id), case.get_template[1])
        )
        zip_file.writestr(
            'Заявление.docx',
            api_download(str(case.user.id), str(case.id), case.get_template[0])
        )

    zip_buffer.seek(0)

    response = HttpResponse(zip_buffer.read(), content_type='application/zip')
    response['Content-Disposition'] = (
        'fattachment; filename={name}.zip'.format(
            name=slugify(f'{case.get_template_display()}_{case}', 'ru')
        )
    )

    return response
    # except Exception as e:
    #     logging.log(e)
    # finally:
    #     return redirect('main:case', pk)


@login_required
def delete_case(request, pk):
    case = get_object_or_404(Case, pk=pk, user=request.user)

    if case.debt_statement and os_path_exists(case.debt_statement.path):
        os_remove(case.debt_statement.path)
    if case.egrn and os_path_exists(case.egrn.path):
        os_remove(case.egrn.path)

    case.delete()
    return redirect('main:profile')


def api_upload(
    user_id: str,
    case_id: str,
    movements_list: List[str],
    plaintiff: dict,
    defendant: dict,
    arrears: float,
    date: str,
    period: str
):
    try:
        response = requests_post(
            settings.API_URL_UPLOAD,
            json={
                'user_id': user_id,
                'case_id': case_id,
                'movements_list': movements_list,
                'plaintiff': plaintiff,
                'defendant': defendant,
                'arrears': arrears,
                'date': date,
                'period': period,
            },
            headers={
                'x-access-token': settings.API_ACCESS_TOKEN
            }
        )
        if response.status_code == 200:
            ...
    except RequestsConnectionError as rce:
        logging.error(f'''
            [Error] Failed to fetch data.
            : {rce}
        ''')


def api_download(user_id, case_id, movements) -> bytes:
    try:
        response = requests_get(
            settings.API_URL_DOWNLOAD,
            json={
                'user_id': user_id,
                'case_id': case_id,
                'movements': movements
            },
            headers={
                'x-access-token': settings.API_ACCESS_TOKEN
            }
        )
        if response.status_code == 200:
            return response.content
    except RequestsConnectionError:
        return None


def api_ready(user_id, case_id, movements) -> dict:
    try:
        response = requests_get(
            settings.API_URL_CHECK,
            json={
                'user_id': user_id,
                'case_id': case_id,
                'movements': movements
            },
            headers={
                'x-access-token': settings.API_ACCESS_TOKEN
            }
        )

        if response.status_code == 200:
            result = response.json().get('ready')
            r = {
                'result': result,
                'message': 'ready' if result else 'wait'
            }
        elif response.status_code in (400, 404):
            r = {
                'result': False,
                'message': 'failed'
            }
        else:
            r = {
                'result': False,
                'message': 'wait'
            }
        return r
    except RequestsConnectionError:
        return {
            'result': False,
            'message': 'lost_connection'
        }


@receiver(post_save, sender=Case)
def create_case_files(sender, instance: Case, **kwargs):
    if not instance.debt_statement:
        return

    data = instance.data

    for case in Case.objects.exclude(id=instance.id):
        if (
            case.data == data and
            case.user == instance.user
        ):
            if instance.debt_statement and os_path_exists(instance.debt_statement.path):
                os_remove(instance.debt_statement.path)
            if instance.egrn and os_path_exists(instance.egrn.path):
                os_remove(instance.egrn.path)
            instance.delete()
            return

    api_upload(
        user_id=str(instance.user.id),
        case_id=str(instance.id),
        movements_list=data['movements'],
        plaintiff={
            'name': data['org_name'],
            'inn': data['org_inn'],
            'ogrn': data['org_ogrn'],
            'kpp': data['org_kpp'],
            'address': data['org_address'],
            'representative': data['org_representative_person']
        },
        defendant={
            'address': data['address'],
            'representative': data['name'],
        },
        arrears=data['amount'],
        date=data['date'],
        period=data['period'],
    )


@login_required
def get_debt_data(request):
    text = ''
    pdf_reader = PdfReader(ContentFile(request.FILES['pdf'].read()))
    text += pdf_reader.pages[0].extract_text()
    text += pdf_reader.pages[-1].extract_text()

    return JsonResponse({'data': [
        ('Период', re_findall(r'за\s(?:(.*))\n', text)[0]),
        # 'org_inn': re_findall(r'ИНН\s(?:(.*))\n', text)[0],
        ('Адрес', re_findall(r'Адрес:\s(?:(.*))\n', text)[0]),
        ('Имя', re_findall(r'Ответственный.*:(.*)\n', text)[0]),
        ('Дата', re_findall(r'Долг\sна\s([0-9.]*)\s', text)[0]),
        ('Сумма', float(re_findall(r'составляет\s([0-9., ]*) руб.', text)[0].replace(' ', '').replace(',', '.')))
    ]})
