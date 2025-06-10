from django import forms
from django.utils.translation import gettext_lazy as _
from .models import LietotajaZinojums, Marsruts, Pietura, Transportlidzeklis, Atsauksme

class TrafficReportForm(forms.ModelForm):
    """
    Form for reporting traffic conditions
    """
    class Meta:
        model = LietotajaZinojums
        fields = ['tips', 'apraksts', 'gps_koordinates', 'marsruts', 'pietura',
                  'transp', 'pasazieru_skaits']
        widgets = {
            'apraksts': forms.Textarea(attrs={'rows': 4}),
        }

class AtsauksmeForm(forms.ModelForm):
    def clean_novērtējums(self):
        value = self.cleaned_data.get('novērtējums')
        if value is not None and value < 1:
            raise forms.ValidationError(_('Rating must be at least 1.'))
        return value

    class Meta:
        model = Atsauksme
        fields = ['teksts', 'novērtējums']
        widgets = {
            'teksts': forms.Textarea(attrs={'rows': 3, 'placeholder': _('Write your review here...')}),
            'novērtējums': forms.NumberInput(attrs={'min': 1, 'max': 5, 'placeholder': _('Rating (1-5)')})
        }