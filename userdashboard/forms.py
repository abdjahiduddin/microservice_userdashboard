from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from accounts.models import CustomUser
from macaddress.fields import MACAddressField
from re import match

#class CustomUserCreateDeviceForm(forms.Form):
class CustomUserCreateDeviceForm(forms.Form):
	class Meta:
		help_text = {
			'macaddress': _('Example: 0123456789ab'),
		}

	def validate_mac(macaddress):
		print('MACADDRESS: ',macaddress)
		#if match("([0-9a-fA-F][0-9a-fA-F]:){5}([0-9a-fA-F][0-9a-fA-F])$",
		#if match("^[a-fA-F0-9:]{17}|[a-fA-F0-9]{12}$",
		#if match("[a-fA-F0-9:]{17}",
		#if match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$",
		if match("[0-9a-f]{2}([-:])[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$",
		macaddress.lower()):
			raise ValidationError("MAC Address format is not correct.")
		else:
			#newmac = ':'.join(macaddress[i:i+2] for i in range(0,12,2))
			#print('NEWMAC: '+newmac)
			return macaddress

	#def clean_macaddress(self):
    #	return self.macaddress

	widget = forms.TextInput(attrs={'class':'form-control'})

	macaddress = forms.CharField(max_length=17,
	min_length=12,validators=[validate_mac],help_text='Ex.:\
	abcdef123456 (WARNING: changing this will change the JWT tokens of topics\
	associated with this device)',widget=widget)
	name = forms.CharField(max_length=20, min_length=4,widget=widget,)
	description = forms.CharField(max_length=50, min_length=4,widget=widget,)
	statuschoices = [
		('active','active'),
		('deactive','deactive'),
	]
	status = forms.ChoiceField(choices=statuschoices,)
	location = forms.CharField(max_length=20, min_length=4,widget=widget,)

class CustomUserCreateTopicForm(forms.Form):
#class CustomUserCreateTopicForm(UserChangeForm):
	class Meta:
		help_text = {
			'macaddress': _('Example: 0123456789ab'),
		}

	widget = forms.TextInput(attrs={'class':'form-control'})

	name = forms.CharField(max_length=20, min_length=4,widget=widget)
	description = forms.CharField(max_length=50, min_length=4,widget=widget,)
	statuschoices = [
		('structured','structured'),
		('semistructured','semi-structured'),
		('unstructured','unstructured'),
	]
	#structure = forms.ChoiceField(choices=statuschoices,)
	##devicechoices = []
	#devices = forms.MultipleChoiceField()

	#currentusermodel = forms.save(commit=False)
	#devices = currentusermodel.devicemacs
	#devicechoices = []
	#for i in devices:
#		devicechoices.append((i['name']))
#	print(devicechoices)
#	connecteddevices = forms.CharField(max_length=20, min_length=4,widget=widget,)
