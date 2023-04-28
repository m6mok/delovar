from django.shortcuts import render


def profile(request):
    context = {}
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
