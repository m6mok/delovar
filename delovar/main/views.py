from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, logout, login
from django.urls import reverse_lazy

from . import forms


@login_required
def profile(request):
    context = {
        'data': [
            {
                'pk': 0,
                'name': '1',
                'surname': '11',
                'nickname': '111',
            },
            {
                'pk': 1,
                'name': '2',
                'surname': '22',
                'nickname': '222',
            },
            {
                'pk': 2,
                'name': '3',
                'surname': '333',
                'nickname': '',
            }
        ],
        'documents': [
            {
                'name': 'Документ 1',
                'url': 'https://ppnm1.ru/Prays_ot_01_04_23.pdf'
            },
            {
                'name': 'Документ 2',
                'url': ''
            },
            {
                'name': 'Документ 3',
                'url': ''
            },
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
