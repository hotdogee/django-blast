from django import forms

class AddMigrationForm(forms.Form):
    username = forms.CharField(label='Your user name', max_length=100)
    password = forms.CharField(label='Your password', max_length=100)
    
# The Organism field should be passed as a keyword, or as a hidden field
#    submission_date
    organism_name = forms.CharField(label='Organism Name')
    organism_id = forms.IntegerField(label='Organism ID')
    jbrowse_url = forms.CharField(label='JBrowse URL')
#    user_id 

