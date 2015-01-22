from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.auth.models import User

class BootStrapPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label=_("Old password"),
                                   widget=forms.PasswordInput({
                                       'class':'form-control',
                                       'placeholder': 'Old password',
                                   })
                                  )
    new_password1 = forms.CharField(label=_("New password"),
                                    widget=forms.PasswordInput({
                                        'class':'form-control',
                                        'placeholder': 'New password',
                                    })
                                   )
    new_password2 = forms.CharField(label=_("New password confirmation"),
                                    widget=forms.PasswordInput({
                                        'class':'form-control',
                                        'placeholder': 'New password',
                                    })
                                  ) 
class InfoChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

