from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse_lazy, reverse
from django.views.generic.edit import FormView
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.db.models import Q
from django.http import JsonResponse

from .forms import CaseForm
from .models import Case


class LoginRequiredMixin:
    """
    Mixin to require login for a view.
    """
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class AdminRequiredMixin:
    """
    Mixin to require admin role for a view.
    """
    def test_func(self):
        return self.is_staff

    @method_decorator(user_passes_test(test_func))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


def case_search(request):
    query = request.GET.get('term', '')
    cases = Case.objects.filter(
        Q(name__icontains=query) |
        Q(address__icontains=query) |
        Q(period__icontains=query) |
        Q(owner=request.user)
    )[:10]

    return JsonResponse([{
        'label': str(case),
        'value': case.pk
    } for case in cases], safe=False)


class CaseView(LoginRequiredMixin, DetailView):
    model = Case
    template_name = 'processor/case.html'
    context_object_name = 'case'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        case = self.get_object()
        context['case'] = [{
            'label': Case._meta.get_field(name).verbose_name,
            'value': getattr(case, name) if name != 'owner' else str(case.owner)
        } for name in (
            'id',
            'owner',
            'name',
            'address',
            'period',
            'payment_amount',
            'format'
        )]
        context['case_name'] = str(case)

        return context


class CaseListView(LoginRequiredMixin, ListView):
    model = Case
    template_name = 'processor/profile.html'
    context_object_name = 'cases'

    def get_queryset(self):
        cases = [
        [{
            'label': Case._meta.get_field(name).verbose_name,
            'value': getattr(case, name)
        } for name in (
            'id',
            'name',
            'address',
            'period',
            'payment_amount',
            'format'
        )] for case in Case.objects.filter(owner=self.request.user)
    ]
        return cases


class AllCasesListView(AdminRequiredMixin, CaseListView):
    template_name = 'processor/cases.html'

    def get_queryset(self):
        cases = [
        [{
            'label': Case._meta.get_field(name).verbose_name,
            'value': getattr(case, name) if name != 'owner' else str(case.owner)
        } for name in (
            'id',
            'owner',
            'name',
            'address',
            'period',
            'payment_amount',
            'format'
        )] for case in Case.objects.all()
    ]
        return cases


class CaseCreateView(LoginRequiredMixin, FormView):
    template_name = 'processor/new_case.html'
    form_class = CaseForm
    success_url = reverse_lazy('processor:profile')

    def post(self, request, *args, **kwargs):
        form = CaseForm(request.POST)
        form.instance.owner = self.request.user
        if form.is_valid():
            case = form.save()
            return redirect(reverse_lazy('processor:profile'))


class AnotherUserCaseCreateView(AdminRequiredMixin, CaseCreateView):
    template_name = 'processor/another_user_new_case.html'

    def get_success_url(self):
        user_pk = self.object.owner.pk
        return reverse('processor:another_profile', args=(user_pk,))
