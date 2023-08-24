from django import forms
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm
)

from .models import CustomUser


class CustomAuthenticationForm(AuthenticationForm):
    inn = forms.CharField(label='ИНН', max_length=12)
    remember_me = forms.BooleanField(
        label='Запомнить меня',
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['inn'].widget.attrs.update({
            'autofocus': True,
            'class': 'form-control'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control'
        })
        self.fields.pop('username')

    def clean(self):
        cleaned_data = super().clean()
        inn = cleaned_data.get('inn')
        password = cleaned_data.get('password')
        remember_me = cleaned_data.get('remember_me')

        if inn is not None and password:
            user_cache = self.authenticate(
                inn=inn,
                password=password,
                remember_me=remember_me
            )
            if user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(user_cache)
        
        return cleaned_data

    def authenticate(self, inn=None, password=None, remember_me=False):
        user = authenticate(request=self.request, username=inn, password=password)

        if user is not None:
            if remember_me:
                login(self.request, user)
            else:
                login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
        
        return user


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['inn', 'email', 'label', 'address', 'leader_name']


class CustomUserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ('inn', 'email', 'label', 'address', 'leader_name'):
            self.fields[name].widget.attrs.update({
                'class': 'form-control'
            })

    class Meta:
        model = CustomUser
        fields = ['inn', 'email', 'label', 'address', 'leader_name']


class PasswordResetForm(forms.Form):
    email = forms.EmailField()
