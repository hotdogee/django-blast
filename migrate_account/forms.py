from django import forms

class AddMigrationForm(forms.Form):
    username = forms.CharField(label='Your user name', max_length=100)
    password = forms.CharField(label='Your password', max_length=100)
    organism_display_name = forms.CharField(label='Organism Name')
    organism_short_name = forms.CharField(label='Organism Short Name')
    organism_id = forms.IntegerField(label='Organism ID')
    jbrowse_url = forms.CharField(label='JBrowse URL')


class ConfirmMigrationForm(forms.Form):
    username = forms.CharField(label='Your user name', max_length=100)
    password = forms.CharField(label='Your password', max_length=100)
    organism_name = forms.CharField(label='Organism Name')
    organism_id = forms.IntegerField(label='Organism ID')
    jbrowse_url = forms.CharField(label='JBrowse URL')

