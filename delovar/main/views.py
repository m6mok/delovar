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
                'name': 'Иванов Иван Иванович',
                'surname': '11',
                'nickname': '111',
            },
            {
                'pk': 1,
                'name': 'Петров Пётр Петрович',
                'surname': '22',
                'nickname': '222',
            },
            {
                'pk': 2,
                'name': 'Яковлев Яков Яковлевич',
                'surname': '333',
                'nickname': '',
            }
        ],
        'documents': [
            {
                'name': 'Документ 1',
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
