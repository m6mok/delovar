from django.shortcuts import render
from django.contrib.auth.decorators import login_required


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
    context = {}
    return render(request, 'main/index.html', context)
