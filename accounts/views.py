from django.shortcuts import render, redirect, get_object_or_404

from django.contrib import auth

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.contrib.auth import login as first_time_login
from django.contrib.auth.decorators import login_required

from accounts.forms import CustomUserSignupForm, CustomUserEditForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from accounts.emailtokens import account_activation_token
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.core.mail import EmailMessage

def signup(request):
	print('SIGNUP!')
	if request.method == 'POST':
		print('inside req met')
		form = CustomUserSignupForm(request.POST)
		if form.is_valid():
			print('valid form')
			user = form.save(commit=False)
			user.is_active = False
			user.is_email_verified = False
			kwargs = {'registering':True}

			user.save(**kwargs)
			try:
				make_email_confirmation(user, request, form)
			except Exception as e:
				print('An excetion has occured: ', e)
				print(type(e))
				print(e.args)

			return HttpResponse('Please confirm your email address to complete the registration')
	else:
		print('Form invalid!')
		form = CustomUserSignupForm()
	return render(request, 'accounts/signup.html', {'form': form})

def make_email_confirmation(user, request, form):
		current_site = get_current_site(request)
		mail_subject = 'Activate Your PTRIoT-EX Account.'
		message = render_to_string('accounts/acc_active_email.html', {
			'user': user,
			'domain': current_site.domain,
			'uid':urlsafe_base64_encode(force_bytes(user.pk)),
			'token':account_activation_token.make_token(user),
		})
		to_email = form.cleaned_data.get('email')
		email = EmailMessage(
					mail_subject, message, to=[to_email]
		)
		email.send()
		print('Please confirm your email address to complete the registration')


def activate(request, uidb64, token):
	print('Activating account...')
	try:
		uid = force_text(urlsafe_base64_decode(uidb64))
		user = get_object_or_404(get_user_model(), pk=uid)
	except(TypeError, ValueError, OverflowError, User.DoesNotExist):
		user = None
	if user is not None and account_activation_token.check_token(user, token):
		user.is_email_verified = True
		user.save()
		first_time_login(request, user)
		return redirect('login')

	else:
		return HttpResponse('Activation link is invalid!')

@login_required
def edit_profile(request):
	if request.method == 'POST':
		form = CustomUserEditForm(request.POST, instance=request.user)

		if form.is_valid():
			form.save()
			return redirect('accountseditprofile')

	else:
		profile = {
					'age':request.user.age,
					'gender':request.user.gender,
					'body_height':request.user.body_height,
					'body_weight':request.user.body_weight,
				}
		print(profile)
		form = CustomUserEditForm(instance=request.user,initial=profile)
		#print('form edit_profile: ',form)
		args = {'form':form}
		return render(request, 'accounts/editprofile.html', args)

"""
TODO: Make the logics of login() and logout() the same as signup!
		Also, give view to the HttpResponse !
"""
def login(request):
	if request.method == 'POST':
		uname = request.POST['username']
		passwd = request.POST['password']
		user =\
			auth.authenticate(username=uname,password=passwd)
		if user is not None:
			auth.login(request,user)
			return redirect('home')
		else:
			errormessage = "Incorret username or password."
			return render(request, 'accounts/login.html', {'error':errormessage})
	else:
		return render(request, 'accounts/login.html')

def logout(request):
	print('Trying to Logging out...')
	if request.method == 'POST':
		print('Logging out...')
		auth.logout(request)
		return redirect('home')

#End of accounts/views.py
