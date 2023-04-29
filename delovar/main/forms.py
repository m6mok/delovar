from django import forms


class LoginForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

    inn = forms.IntegerField(label='ИНН')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)
