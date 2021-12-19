from django import forms
from .models import Devices, Script_logs


SITES_CHOICES = [
    ('VER', "Veracruz"), ('GDL', "Guadalajara"),
    ('QRO', "Queretaro"), ('TOL', "Toluca"), ('CLN', "Culiacan")
    , ('HMO', "Hermosillo"), ('LEON', "Leon"), ('TOR', "Torreon")
]

'''
class LoadChoices(forms.ModelForm):

    def __init__(self, all_list, *args, **kwargs):
        super(LoadChoices, self).__init__(*args, **kwargs)
        self.fields['name'] = forms.ChoiceField(choices=tuple([all_list]))

    class Meta:
        model = models.RatingSheet
        fields = ('name', )


class MyForm(forms.Form):
         def __init__(self, *args, **kwargs):
                super(MyForm, self).__init__(*args, **kwargs)
                get_my_choices=[ (x.file_location, Devices.objects.get(ip_address=x.host_id).hostname+'-'+str(x.data_date)) for x in Script_logs.objects.filter(script_type='mcastflow').all()]
                self.fields['my_choice_field'] = forms.ChoiceField( choices=get_my_choices )
'''

class NameForm(forms.Form):
    your_ip = forms.CharField(label='IP Address', max_length=100
                            , widget=forms.TextInput( attrs= {'class':'form-control'}) )
    '''alternativas = forms.ChoiceField(label="",
                                choices=[ (x.ip_address, x.hostname) for x in Devices.objects.all()],
                                initial='',
                                widget=forms.Select(),
                                required=True)'''


class IPForm(forms.Form):
    #your_ip = forms.CharField(label='IP Address', max_length=100)
    alternativas = forms.ModelChoiceField(required=True
                                       , widget=forms.Select(attrs= {'class':'form-control'})
                                       , queryset=Devices.objects.all()
                                       ,to_field_name="hostname")

class IP_XR_Form(forms.Form):
    your_ip = forms.CharField(label='IP Address', max_length=100)

class d3Form(forms.Form):
    sites = forms.ChoiceField(choices = SITES_CHOICES, label="Mega Sites"
                            , initial='', widget=forms.Select(attrs= {'class':'form-control'})
                            , required=True)

class d3Form2(forms.Form):
    sites = forms.ChoiceField(choices = SITES_CHOICES, label="Mega Sites"
                            , initial='', widget=forms.Select(attrs= {'class':'form-control'})
                            , required=True)

class TrafficForm(forms.Form):
    devices = forms.ModelChoiceField(required=True
                                       , widget=forms.Select( attrs= {'class':'form-control'})
                                       , queryset=Devices.objects.all()
                                       ,to_field_name="hostname")

class CompareForm(forms.Form):
    #your_ip = forms.CharField(label='IP Address', max_length=100)
    alternativas1 = forms.ModelChoiceField(required=True
                                       , widget=forms.Select( attrs= {'class':'form-control'})
                                       , queryset=Script_logs.objects.filter(script_type='mcastflow').all()
                                       ,to_field_name="file_location")
    alternativas2 = forms.ModelChoiceField(required=True
                                       , widget=forms.Select( attrs= {'class':'form-control'})
                                      , queryset=Script_logs.objects.filter(script_type='mcastflow').all()
                                      ,to_field_name="file_location")


class LoginForm(forms.Form):
    your_email = forms.CharField(label='E-mail', max_length=100,
                                 widget=forms.TextInput( attrs= {'class':'form-control'}) )
    your_password = forms.CharField(label='Password', max_length=100,
                                  widget=forms.PasswordInput( attrs= {'class':'form-control'}) )
