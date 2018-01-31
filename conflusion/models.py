#!/usr/bin/env false

# Conflusion Membership Tracker - Main Database Schema File

'''
This file essentially provides the schema for the database for the system.

Additional database schema for other potential functionalities of this whole
system that are tentative or proposed are in separate "models_xxx.py" files.

'''

# -----------------------------------------------------------------------------

from django.db import models
from django.contrib.auth.models import User  # for extending the auth table

# This class extends the 'auth_user' table provided by the Django auth package.
# It contains all the basic information about and set by the user.
class Users(models.User):
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
  

# -----------------------------------------------------------------------------
# This add the "Certifications" schema
import models_certs
