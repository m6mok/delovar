from django import forms
from django.core.validators import FileExtensionValidator

from .models import Case


class LoginForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

    inn = forms.IntegerField(label='ИНН')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)


class NewCaseForm(forms.ModelForm):
    class Meta:
        model = Case
        fields = ['template', 'debt_statement', 'egrn']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        
        super().__init__(*args, **kwargs)
        for name in ('template', 'debt_statement', 'egrn'):
            self.fields[name].widget.attrs.update({
                'class': 'form-control'
            })

        if user:
            self.instance.user = user

        self.fields['template'].required = True

        self.fields['debt_statement'].validators.append(FileExtensionValidator(['pdf']))
        self.fields['debt_statement'].required = True

        self.fields['egrn'].validators.append(FileExtensionValidator(['pdf']))
        self.fields['egrn'].required = False


class CaseDetailForm(forms.ModelForm):
    class Meta:
        model = Case
        fields = ['debt_statement', 'egrn']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        
        super().__init__(*args, **kwargs)
        for name in ('debt_statement', 'egrn'):
            self.fields[name].widget.attrs.update({
                'class': 'form-control'
            })

        if user:
            self.instance.user = user

        self.fields['debt_statement'].validators.append(FileExtensionValidator(['pdf']))
        self.fields['debt_statement'].required = True

        self.fields['egrn'].validators.append(FileExtensionValidator(['pdf']))
        self.fields['egrn'].required = False
