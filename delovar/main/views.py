from django.shortcuts import render
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.views.generic.edit import FormView

from user.forms import CustomAuthenticationForm


def about(request):
    context = {}
    return render(request, 'main/about.html', context)


def prices(request):
    context = {}
    return render(request, 'main/prices.html', context)


def faq(request):
    context = {}
    return render(request, 'main/faq.html', context)


class IndexView(FormView):
    template_name = 'main/index.html'
    form_class = CustomAuthenticationForm
    success_url = reverse_lazy('processor:profile')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
