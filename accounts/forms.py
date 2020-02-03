from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser
from macaddress.fields import MACAddressField

class CustomUserSignupForm(UserCreationForm):
	username = forms.CharField(max_length=30, min_length=4)
	email = forms.EmailField(max_length=200, help_text='Required')

	class Meta:
		model = CustomUser
		fields = ('username', 'email', 'password1', 'password2', )

class CustomUserEditForm(UserChangeForm):
	class Meta:
		model = CustomUser
		fields = (
					'age',
					'gender',
					'body_height',
					'body_weight',
					'password'
		)
		exclude = (
					'email',
					'username',
		)

	genderchoices = [
		('male','male'),
		('female','female'),
	]
	gender = forms.ChoiceField(choices=genderchoices)
	age = forms.DecimalField()
	body_height = forms.DecimalField(min_value=1,decimal_places=2,label="Body\
	height (cm):")
	body_weight = forms.DecimalField(min_value=1,decimal_places=2,label="Body\
	weight (kg):")

class CustomUserEditFormForAdmin(UserChangeForm):
	genderchoices = [
		('male','male'),
		('female','female'),
	]
	gender = forms.ChoiceField(choices=genderchoices)

	class Meta:
		model = CustomUser
		fields = (
					'username',
					'password',
					'package',
					'email',
					'devicemacs',
					'topics',
					'gender',
					'age',
					'body_height',
					'body_weight',
					'is_email_verified',
					'is_active',
		)

class CustomUserPasswordChangeForAdmin(UserChangeForm):
	class Meta:
		model = CustomUser
		fields = (
					'password',
		)

	def save(self, commit=True):
		"""
		Saves the new password.
		"""
		password = self.cleaned_data["password1"]
		self.user.myuser.set_password(password)
		if commit:
			self.user.myuser.save()
		return self.user.myuser
