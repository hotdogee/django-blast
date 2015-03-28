from django import forms
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm, AuthenticationForm
from django.utils.translation import ugettext, ugettext_lazy as _
from .models import Profile

class BootstrapAuthenticationForm(AuthenticationForm):
    username = forms.CharField(max_length=254,
                               widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'User name'}))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder':'Password'}))


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
    first_name = forms.CharField(label=_(u'First name'), max_length=30, required=True)
    last_name = forms.CharField(label=_(u'Last name'), max_length=30, required=True)
    email = forms.EmailField(label=_(u'Email'),required=True)
    institution = forms.CharField(label=_(u'Institution'),required=True)

    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'email', 'institution']
    
    def __init__(self, *args, **kw):
        super(InfoChangeForm, self).__init__(*args, **kw)
        self.fields['first_name'].initial = self.instance.user.first_name
        self.fields['first_name'].widget.attrs.update({'class' : 'form-control'})
        self.fields['last_name'].initial = self.instance.user.last_name
        self.fields['last_name'].widget.attrs.update({'class' : 'form-control'})
        self.fields['email'].initial = self.instance.user.email
        self.fields['email'].widget.attrs.update({'class' : 'form-control'})
        self.fields['institution'].initial = self.instance.institution
        self.fields['institution'].widget.attrs.update({'class' : 'form-control'})

    def save(self, *args, **kw):
        super(InfoChangeForm, self).save(*args, **kw)
        self.instance.user.first_name = self.cleaned_data.get('first_name')
        self.instance.user.last_name = self.cleaned_data.get('last_name')
        self.instance.user.email = self.cleaned_data.get('email')
        self.instance.user.save()
        self.instance.institution = self.cleaned_data.get('institution')
        self.instance.save()


class GetInstitutionForm(forms.ModelForm):
    institution = forms.CharField(label=_(u'Institution'),required=True)

    class Meta:
        model = Profile
        fields = ['institution']
    
    def __init__(self, *args, **kw):
        super(GetInstitutionForm, self).__init__(*args, **kw)
        self.fields['institution'].widget.attrs.update({'class': 'form-control', 'placeholder': 'e.g. National Agricultural Library'})


class RegistrationForm(UserCreationForm):
    first_name = forms.RegexField(label=_("First name"), max_length=30, required=True,
        regex=r'^[\w.-]+$',
        help_text=_("Required. 30 characters or fewer. Letters, digits and /./-/_ only."),
        error_messages={'invalid': _("This value may contain only letters, numbers and /./-/_ characters.")}
    )
    last_name = forms.RegexField(label=_("Last name"), max_length=30, required=True,
        regex=r'^[\w.-]+$',
        help_text=_("Required. 30 characters or fewer. Letters, digits and /./-/_ only."),
        error_messages={'invalid': _("This value may contain only letters, numbers and /./-/_ characters.")}
    )
    email = forms.EmailField(label=_(u'Email'),required=True)
    institution = forms.RegexField(label=_("Institution"), max_length=100, required=True,
        regex=r'^[\w.-]+$',
        help_text=_("Required. 30 characters or fewer. Letters, digits and /./-/_ only."),
        error_messages={'invalid': _("This value may contain only letters, numbers and /./-/_ characters.")}
    )

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        if len(password1) < 8:
            raise forms.ValidationError('Password must be at least 8 characters long.')
        return password1

    def __init__(self, *args, **kw):
        super(RegistrationForm, self).__init__(*args, **kw)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        self.fields['first_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['institution'].widget.attrs.update({'class': 'form-control', 'placeholder': 'e.g. National Agricultural Library'})
