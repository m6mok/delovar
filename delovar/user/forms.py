from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm
)
from django.core.validators import FileExtensionValidator
from django.contrib.auth import authenticate, login

from .models import CustomUser


USER_FIELDS = [
    'inn',
    'ogrn',
    'kpp',
    'label',
    'address',
    'representative_person',
    'mkd',
    'egrul'
]


INFO_FIELDS = [
    'label',
    'address',
    'representative_person'
]


DOCUMENT_FIELDS = [
    'mkd',
    'egrul'
]


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
        fields = USER_FIELDS


class CustomUserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in USER_FIELDS:
            self.fields[name].widget.attrs.update({
                'class': 'form-control'
            })

    class Meta:
        model = CustomUser
        fields = USER_FIELDS
    

class CustomUserDocumentsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in DOCUMENT_FIELDS:
            self.fields[name].widget.attrs.update({
                'class': 'form-control'
            })
            self.fields[name].validators.append(FileExtensionValidator(['pdf']))
            self.fields[name].required = False
        for name in INFO_FIELDS:
            self.fields[name].widget.attrs.update({
                'class': 'form-control'
            })

    class Meta:
        model = CustomUser
        fields = INFO_FIELDS + DOCUMENT_FIELDS


class PasswordResetForm(forms.Form):
    email = forms.EmailField()
