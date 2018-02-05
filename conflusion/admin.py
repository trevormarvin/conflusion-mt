#!/bin/false


# for over riding the default 'User' model
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
admin.site.register(User, UserAdmin)
# https://docs.djangoproject.com/en/2.0/topics/auth/customizing/#extending-the-existing-user-model
