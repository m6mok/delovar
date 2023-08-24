from django import forms
from .models import Case


class CaseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CaseForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = Case
        fields = ['name', 'address', 'period', 'payment_amount', 'format']
