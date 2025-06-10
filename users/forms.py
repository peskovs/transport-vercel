from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import gettext_lazy as _
from .models import User

class UserRegistrationForm(UserCreationForm):
    """
    Lietotāja reģistrācijas forma
    """
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'talrunis', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Papildus lauku opcijas
        self.fields['first_name'].required = False
        self.fields['last_name'].required = False
        self.fields['talrunis'].required = False
        # Obligāto lauku opcijas
        self.fields['email'].required = True
        # Placeholderi
        self.fields['username'].widget.attrs.update({'placeholder': _('Username')})
        self.fields['first_name'].widget.attrs.update({'placeholder': _('First name')})
        self.fields['last_name'].widget.attrs.update({'placeholder': _('Last name')})
        self.fields['email'].widget.attrs.update({'placeholder': _('Email')})
        self.fields['talrunis'].widget.attrs.update({'placeholder': _('Phone')})
        self.fields['password1'].widget.attrs.update({'placeholder': _('Password')})
        self.fields['password2'].widget.attrs.update({'placeholder': _('Confirm password')})

class UserLoginForm(forms.Form):
    """
    Lietotāja pieteikšanās forma
    """
    username = forms.CharField(label=_('Username'), widget=forms.TextInput(attrs={'placeholder': _('Username')}))
    password = forms.CharField(label=_('Password'), widget=forms.PasswordInput(attrs={'placeholder': _('Password')}))
    remember_me = forms.BooleanField(label=_('Remember me'), required=False)

class UserProfileForm(forms.ModelForm):
    """
    Lietotāja profila rediģēšanas forma
    """
    def clean_username(self):
        username = self.cleaned_data['username']
        user_qs = User.objects.filter(username=username)
        if self.instance.pk:
            user_qs = user_qs.exclude(pk=self.instance.pk)
        if user_qs.exists():
            from django.utils.translation import gettext_lazy as _
            raise forms.ValidationError(_('This username is already taken. Please choose another.'))
        return username

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'talrunis']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Padarīt epastu un lietotājvārdu obligātu
        self.fields['email'].required = True
        self.fields['username'].required = True
        self.fields['username'].widget.attrs.update({'placeholder': _('Username')})