from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, logout, login
from django.urls import reverse_lazy

from . import forms


@login_required
def profile(request):
    context = {
        'documents': [
            {'name': 'Заявление о выдаче судебного приказа', 'auto': True, 'loaded': False},
            {'name': 'Выписка из ЕГРН', 'auto': False, 'loaded': True, 'type': '.pdf'},
            {'name': 'Расчёт задолжности', 'auto': False, 'loaded': False, 'type': '.xlsx'},
            {'name': 'Выписка из ЕГРЮЛ', 'auto': True, 'loaded': False},
            {'name': 'Договор управления МКД', 'auto': True, 'loaded': False},
            {'name': 'Квитанция об оплате госпошлины', 'auto': True, 'loaded': True}
        ],
        'samples': [
            {
                'name': 'Взыскать задолжность с помощью судебного приказа',
                'url': 'https://view.officeapps.live.com/op/embed.aspx?src={}'.format('https://cn57892.tmweb.ru/document1.docx')
            }
        ]
    }
    return render(request, 'main/profile.html', context)


def profile_login(request):
    form = None
    if request.method == 'POST':
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(username=form.data['inn'], password=form.data['password'])
            if user:
                login(request, user)
                return redirect(reverse_lazy('main:profile'))
    context = {}
    if form:
        context['form'] = form
    else:
        context['form'] = forms.LoginForm()
    return render(request, 'main/login.html', context)


def profile_logout(request):
    logout(request)
    context = {}
    return render(request, 'main/logout.html', context)


def about(request):
    context = {}
    return render(request, 'main/about.html', context)


def prices(request):
    context = {}
    return render(request, 'main/prices.html', context)


def faq(request):
    context = {}
    return render(request, 'main/faq.html', context)


def index(request):
    form = forms.LoginForm(request.POST)
    context = {}
    if form:
        context['form'] = form
    else:
        context['form'] = forms.LoginForm()
    return render(request, 'main/index.html', context)
