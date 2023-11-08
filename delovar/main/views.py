from zipfile import ZipFile
from io import BytesIO
from os.path import exists as os_path_exists
from os import remove as os_remove

from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django.views.generic import TemplateView
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


def file_ready(data, _settings) -> bool:
    try:
        response = requests_get(
            settings.API_URL_CHECK,
            json={
                'data': data,
                'settings': _settings
            },
            headers={
                'x-access-token': settings.API_ACCESS_TOKEN
            }
        )
        if response.status_code == 200:
            return response.json().get('result')
        elif response.status_code == 404:
            api(data, _settings)
    except RequestsConnectionError:
        return False


def file_download(data, _settings) -> bytes:
    try:
        response = requests_get(
            settings.API_URL_DOCUMENT,
            json={
                'data': data,
                'settings': _settings
            },
            headers={
                'x-access-token': settings.API_ACCESS_TOKEN
            }
        )
        if response.status_code == 200:
            return response.content
    except RequestsConnectionError:
        return None


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
        'statement': file_ready(*case.statement_data),
        'receipt': file_ready(*case.receipt_data)
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
            print(case)
            # if case:
            #     return redirect('main:case', case.id)
            # else:
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
    return JsonResponse({'success': file_ready(*case.receipt_data)})


@login_required
def check_statement(request, pk: str):
    case = get_object_or_404(Case, pk=pk, user=request.user)
    return JsonResponse({'success': file_ready(*case.statement_data)})


@login_required
def check_upload(request, pk: str):
    return JsonResponse({'success': upload_ready(pk, request.user)})


def upload_ready(pk: str, user) -> bool:
    case = get_object_or_404(Case, pk=pk, user=user)
    return bool(
        case.debt_statement and
        case.egrn and
        case.user.mkd and
        case.user.egrul and
        file_ready(*case.statement_data) and
        file_ready(*case.receipt_data)
    )


@login_required
def create_document_pack(request, pk: str):
    case = get_object_or_404(Case, pk=pk, user=request.user)

    if not upload_ready(pk, request.user):
        return JsonResponse({'message': 'Some files are not ready'})

    zip_buffer = BytesIO()

    with ZipFile(zip_buffer, 'w') as zip_file:
        zip_file.write(case.debt_statement.path, 'Расчеты по задолженности.pdf')
        zip_file.write(case.egrn.path, 'Выписка из ЕГРН.pdf')
        zip_file.write(case.user.mkd.path, 'Договор управления МКД.pdf')
        zip_file.write(case.user.egrul.path, 'Выписка из ЕГРЮЛ.pdf')
        zip_file.writestr(
            'Квитанция об уплате госпошлины.pdf',
            file_download(*case.receipt_data)
        )
        zip_file.writestr(
            'Заявление.docx',
            file_download(*case.statement_data)
        )

    zip_buffer.seek(0)

    response = HttpResponse(zip_buffer.read(), content_type='application/zip')
    response['Content-Disposition'] = (
        'fattachment; filename={name}.zip'.format(name=slugify(str(case), 'ru'))
    )

    return response


@login_required
def delete_case(request, pk):
    case = get_object_or_404(Case, pk=pk, user=request.user)

    if case.debt_statement and os_path_exists(case.debt_statement.path):
        os_remove(case.debt_statement.path)
    if case.egrn and os_path_exists(case.egrn.path):
        os_remove(case.egrn.path)

    case.delete()
    return redirect('main:profile')


def api(data, _settings):
    try:
        response = requests_post(
            settings.API_URL_DOCUMENT,
            json={
                'data': data,
                'settings': _settings
            },
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


@receiver(post_save, sender=Case)
def create_case_files(sender, instance: Case, **kwargs):
    if not instance.debt_statement:
        return

    receipt_data = instance.receipt_data
    statement_data = instance.statement_data

    for case in Case.objects.exclude(id=instance.id):
        if (
            case.receipt_data == receipt_data and
            case.statement_data == statement_data and
            case.user == instance.user
        ):
            if instance.debt_statement and os_path_exists(instance.debt_statement.path):
                os_remove(instance.debt_statement.path)
            if instance.egrn and os_path_exists(instance.egrn.path):
                os_remove(instance.egrn.path)
            instance.delete()
            return

    api(*receipt_data)
    api(*statement_data)
