from zipfile import ZipFile
from io import BytesIO
from os.path import exists as os_path_exists
from os import remove as os_remove

from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django.views.generic import TemplateView
from django.http import JsonResponse, HttpResponse
from requests.exceptions import ConnectionError as RequestsConnectionError
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import login # не трогать
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from requests import get as requests_get
from transliterate import slugify
from django.urls import reverse_lazy
from django.conf import settings

from user.forms import CustomAuthenticationForm, CustomUserDocumentsForm
from .models import (
    Case,
    receipt as receipt_request,
    statement as statement_request
)
from .forms import NewCaseForm


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


def file_ready(case_id: str, movements: str) -> bool:
    try:
        response = requests_get(
            settings.API_URL_CHECK,
            json={
                'case_id': str(case_id),
                'movements': movements
            },
            headers={
                'x-access-token': settings.API_ACCESS_TOKEN
            }
        )
        if response.status_code == 200:
            return response.json().get('result')
        elif response.status_code == 404:
            if movements == 'statement':
                statement_request(get_object_or_404(Case, pk=case_id))
            elif movements == 'receipt':
                receipt_request(get_object_or_404(Case, pk=case_id))
    except RequestsConnectionError:
        return False


def file_download(case_id: str, movements: str) -> bytes:
    try:
        response = requests_get(
            settings.API_URL_DOCUMENT,
            json={
                'case_id': str(case_id),
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


@login_required
def case_detail(request, pk: str):
    case = get_object_or_404(Case, pk=pk, user=request.user)

    if request.method == 'POST':
        form = NewCaseForm(request.POST, request.FILES, instance=case)
        if form.is_valid():
            case = form.save()
    else:
        form = NewCaseForm(instance=case)

    context = {
        'case': case,
        'form': form,
    }
    
    try:
        context.update({
            'statement': file_ready(pk, 'statement_magistrate'),
            'receipt': file_ready(pk, 'receipt')
        })
    except RequestsConnectionError:
        ...

    return render(request, 'main/case.html', context)


class CaseListView(ListView):
    model = Case
    template_name = 'main/cases.html'
    context_object_name = 'cases'


@login_required
def new_case(request):
    if request.method == 'POST':
        form = NewCaseForm(request.POST, request.FILES)
        if form.is_valid():
            case: Case = form.save(commit=False)
            case.user = request.user
            case.save()
            return redirect('main:case', case.id)
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
    return JsonResponse({'success': file_ready(pk, 'receipt')})


@login_required
def check_statement(request, pk: str):
    return JsonResponse({'success': file_ready(pk, 'statement_magistrate')})


@login_required
def create_document_pack(request, pk: str):
    case = get_object_or_404(Case, pk=pk, user=request.user)

    try:
        if not (
            case.debt_statement and
            case.egrn and
            case.user.mkd and
            case.user.egrul and
            file_ready(pk, 'statement_magistrate') and
            file_ready(pk, 'receipt')
        ):
            return JsonResponse({'message': 'Some files are not ready'})
    except RequestsConnectionError:
        return JsonResponse({'message': 'Server is not pending'})

    zip_buffer = BytesIO()

    with ZipFile(zip_buffer, 'w') as zip_file:
        zip_file.write(case.debt_statement.path, 'Расчеты по задолженности.pdf')
        zip_file.write(case.egrn.path, 'Выписка из ЕГРН.pdf')
        zip_file.write(case.user.mkd.path, 'Договор управления МКД.pdf')
        zip_file.write(case.user.egrul.path, 'Выписка из ЕГРЮЛ.pdf')
        zip_file.writestr(
            'Квитанция об уплате госпошлины.pdf',
            file_download(pk, 'receipt')
        )
        zip_file.writestr(
            'Заявление.docx',
            file_download(pk, 'statement_magistrate')
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
