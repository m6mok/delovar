from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.core.mail import send_mail
from django.db.models import Q
from django.conf import settings
from django.urls import reverse_lazy

from .models import CustomUser
from .forms import (
    CustomUserCreationForm,
    CustomUserForm,
    PasswordResetForm
)
from .decorators import admin_required


@admin_required
def user_list(request):
    users = CustomUser.objects.all()

    query = request.GET.get('q', '')
    if query:
        users = users.filter(
            Q(inn__icontains=query) |
            Q(email__icontains=query) |
            Q(label__icontains=query) |
            Q(address__icontains=query) |
            Q(leader_name__icontains=query)
        )

    users = [
        [{
            'label': CustomUser._meta.get_field(name).verbose_name,
            'value': user.__dict__[name]
        } for name in (
            'id',
            'inn',
            'email',
            'label',
            'address',
            'leader_name',
            'is_active',
            'is_staff'
        )] for user in users
    ]

    return render(
        request,
        'user/list.html',
        {
            'users': users,
            'q': query
        }
    )


@admin_required
def user_search(request):
    query = request.GET.get('term', '')
    users = CustomUser.objects.filter(
        Q(inn__icontains=query) |
        Q(email__icontains=query) |
        Q(label__icontains=query) |
        Q(address__icontains=query) |
        Q(leader_name__icontains=query)
    )[:10]

    return JsonResponse([{
        'label': str(user),
        'value': user.pk
    } for user in users], safe=False)


@admin_required
def register_user(request):
    if request.method == 'POST':
        form = CustomUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect(reverse_lazy('user:list'))
    else:
        form = CustomUserForm()
    return render(request, 'user/register.html', {'form': form})


@admin_required
def edit_user(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    
    if request.method == 'POST':
        form = CustomUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('list')  # Перенаправление на список пользователей
    else:
        form = CustomUserForm(instance=user)
    
    return render(request, 'user/edit.html', {'user': user, 'form': form})


def password_reset(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data['email']
            user = CustomUser.objects.get(email=user_email)
            # Генерация нового пароля и отправка на почту
            new_password = CustomUser.objects.make_random_password()
            user.set_password(new_password)
            user.save()

            send_mail(
                'Password Reset',
                f'Your new password: {new_password}',
                settings.EMAIL_HOST_USER,
                [user_email],
                fail_silently=False,
            )

            return redirect('login')  # Перенаправление на страницу входа
    else:
        form = PasswordResetForm()
    return render(request, 'user/password_reset.html', {'form': form})
