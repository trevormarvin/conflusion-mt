#!/usr/bin/env false

# Conflusion Membership Tracker - Main Database Schema File

'''
This file essentially provides the schema for the database for the system.

Additional database schema for other potential functionalities of this whole
system that are tentative or proposed are in separate "models_xxx.py" files.

'''

# -----------------------------------------------------------------------------

from django.db import models
from django.contrib.auth.models import AbstractUser  # for extending the auth table
from django.contrib.auth.models import Group as AbstractGroup # mimicing above import

# -------------------------------------------------
# This class extends the 'auth_user' table provided by the Django auth package.
# It contains all the basic information about and set by the user.
class User(AbstractUser):
  '''
  https://docs.djangoproject.com/en/2.0/ref/contrib/auth/#django.contrib.auth.models.User
  
  django.contrib.auth.models.User already contains certain fields:
  
  username = models.CharField(max_length = 191)
  first_name = models.CharField(max_length = 30, blank = True)
  last_name = models.CharField(max_length = 150, blank = True)
  email = models.EmailField(blank = True)
  password = models.PASSWORD
  groups = models.ManyToManyField(models.Group)
  user_permissions = models.ManyToManyField(models.Permission)
  is_staff = models.BooleanField()
  is_active = models.BooleanField()
  is_superuser = models.BooleanField()
  last_login = models.DateTimeField()
  date_joined = models.DateTimeField()
  '''
  
  expire = models.DateField(null = True)
  # expiration of all membership priveleges, otherwise use "Certifications" to
  # tie expirations of particular priveleges

'''
Documentation at:
https://docs.djangoproject.com/en/2.0/topics/auth/customizing/#substituting-a-custom-user-model
...says that the following:

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
admin.site.register(User, UserAdmin)

...needs to be put in the "admin.py" file for overriding the User model.
'''

# -------------------------------------------------
'''
PROPOSED:  A member's membership level is stored in the Django 'Group' model,
which is extended to handle some back-office accounting of such. -TM
'''

# extend the 'Group' model with some more fields
class Group(AbstractGroup):
  '''
  https://docs.djangoproject.com/en/2.0/ref/contrib/auth/#group-model
  
  django.contrib.auth.models.Group already contains certain fields:
  
  name = models.CharField(max_length = 80)
  permissions = ManyToManyField(Permission)
  
  '''
  expire = models.DateField(null = True)
  # expiration of this membership level
  # (checking of the expiration date will need to be included into functions
  # that determine 'Group' membership, or a separate process will need to
  # regularly pass through the table and delete/disable all expired memberships)



# -----------------------------------------------------------------------------
# This add the "Certifications" schema
import models_certs
