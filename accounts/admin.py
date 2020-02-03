from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserSignupForm, CustomUserEditForm,\
    CustomUserEditFormForAdmin, CustomUserPasswordChangeForAdmin
from django.urls import path

from .models import CustomUser

class CustomUserAdmin(UserAdmin):
#class CustomUserAdmin(admin.ModelAdmin):
    #add_form = CustomUserSignupForm
    fieldsets = None
    form = CustomUserEditFormForAdmin
    model = CustomUser
    list_display =\
    ['username','email','is_email_verified','is_active',]
    #change_password_form = CustomUserPasswordChangeForAdmin
    #password_change_template = CustomUserPasswordChangeForAdmin

admin.site.register(CustomUser, CustomUserAdmin)
