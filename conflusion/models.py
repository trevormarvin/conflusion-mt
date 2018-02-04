#!/usr/bin/env false

# Conflusion Membership Tracker - Main Database Schema File

'''
This file essentially provides the schema for the database for the system.

Additional database schema for other potential functionalities of this whole
system that are tentative or proposed are in separate "models_xxx.py" files.

'''

# -----------------------------------------------------------------------------
# Main Django member/user tables used for membership

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

# --------------- Tables for Certifications for Access or Use -----------------

'''
"Certifications" are for enumerating the equipment or skills that require
special approval for access.  A certification may be related to a particular
physical item, or may be referencing a skill necessary to do a particular
activity.  A certification may also be a specific membership level, or
priveleges related to a particular membership level.
'''

class Certifications(models.Model):
  index = models.AutoField(primary_key = True)
  
  name = models.CharField(max_length = 50,
                          null = False,
                          unique = True)
  # this is the name of the resource or skill that is being certified
  
  code = models.CharField(max_length = 16,
                          null = True,
                          unique = True)
  # (If it exists, it must be unique.)
  # This is the code looked up for a particular access device
  
  parent = models.ForeignKey('self',
                             null = True,
                             on_delete = models.CASCADE)
  # If this certification is a subset or under another certification, this
  # field is a reference to the parent certification.  If the parent
  # certification lapses or is invalid for a particular user, then this
  # certification should be considered invalid for the user.
  
  comments = models.TextField(null = True)
  # comments about the particular certification
  
  ml_based = models.ForeignKey(Group,
                               null = True,
                               on_delete = models.SET_NULL)
  # "Membership Level Based"  If access to a particular permission is implicitly
  # granted by a particular membership level, then this is a refernce to the
  # 'Group' whose membership in implicitly grants this certification.
  
  logaccess = models.BooleanField(default = False)
  # Whether to log access to the certification for each query.  e.g.  If the
  # certification is access to the front door, then this could specify that
  # a particular user requested (and presumably received) access to unlock the
  # door.  The access request goes to another table, "CertAccessLog".
  
  logfailed = models.BooleanField(default = False)
  # If 'logaccess' is set, this will set to log failed access attempts.  These
  # failed access attempts will be limited to where the user has an access
  # device (like a prox card), but is not certified for the particular access.
  # Access attempts with invalid or credentials that are not in the database
  # are not logged as there is no user account to attribute them to.
  
  show = models.PositiveIntegerField(default = 0)
  # When displaying a user's access priveleges on a particular interface, this
  # value will act as a threshhold for which certifications will be shown.
  # For example, when a user initially checks in and provides credential (e.g.
  # swipes their access card), the kiosk may show what access priveleges the
  # user has.  This will allow not showing too many priveleges in this context.
  # Lower number are higher priority to show.  Anything at level zero would be
  # for showing in all situations.  The main check in kiosk may show priveleges
  # with a level of 2 or lower, for example.
  
  
# --------------------------------
'''
This next table tracks the certifications that a particular user has.
'''

class Certified(models.Model):
  index = models.AutoField(primary_key = True)
  
  userid = models.ForeignKey(User,
                             on_delete = models.CASCADE,
                             related_name = 'userid')
  # the user with the certification
  
  cert = models.ForeignKey(Certifications,
                           on_delete = models.CASCADE)
  # the certification that the user has
  
  certby = models.ForeignKey(User,
                             on_delete = models.SET_NULL,
                             related_name = 'certby',
                             null = True)
  # the user that authorized the certitification
  certified = models.DateField(null = False)
  # the date that the certification was authorized
  expire = models.DateField(null = True)
  # when the certification expires, null if it never expires

  certifier = models.BooleanField(default = False)
  # whether the user is authorized to certify other users
  
  suspended = models.BooleanField(default = False)
  # whether the certification is suspended, temporarily or otherwise
  # This will presumably be adjustable by anyone who has 'certifier'
  # authorization for a particular certification.
  
  countdown = models.PositiveIntegerField(null = True)
  # if there is a limited number of usages allowed for a particular 
  # certification, this is to be the number of allowed uses remaining, null if
  # not limited
  
  comments = models.TextField(null = True)
  # comments about the particular certification
  
  
  class Meta:
    unique_together = ('cert', 'userid', 'certby')


# --------------------------------
'''
This next logs individual accesses to a certified resource
'''

class CertAccessLog(models.Model):
  index = models.AutoField(primary_key = True)
  
  resource = models.ForeignKey(Certifications,
                               null = True,
                               on_delete = models.CASCADE)
  # the resource that the log entry is for
  
  timestamp = models.DateTimeField(auto_now_add = True)
  # this automatic populating field is the time of the access log event
  
  userid = models.ForeignKey(User,
                             null = True,
                             on_delete = models.SET_NULL)
  # this identifies the user that requested the access
  # (We are not relying on the 'certid' field to identify the user, as the user
  # may not be certified and we want to log a failed access attempt.)
  
  certid = models.ForeignKey(Certified,
                             on_delete = models.SET_NULL,
                             null = True)
  # this links back to the certification that allowed the access, null if access
  # was denied
  
  quantity = models.DecimalField(max_digits = 6,
                                 decimal_places = 2,
                                 null = True)
  # for particular access logging that aims to record a quantity of something,
  # this field records the quantity of usage to a resource
  
  failed = models.BooleanField(default = False)
  # if the log entry is for a failed attempt


# --------------------- Tables for Controlling Access Cards -------------------

'''
This is a table for tracking access devices, be they swipe cards, proximity
cards, or anything else.
'''

class AccessCards(models.Model):
  index = models.AutoField(primary_key = True)
    
  cardid = models.CharField(max_length = 128,
                            null = False,
                            unique = True)
  # unique identifier of an access card or device
  
  userid = models.ForeignKey(User,
                             on_delete = models.CASCADE)
  # user that the access card belongs to
  
  suspended = models.BooleanField(default = False)
  # whether the access device is suspended, temporarily or otherwise
  
  expire = models.DateField(null = True)
  # when the access card expires, null if it never expires
  
  countdown = models.PositiveIntegerField(null = True)
  # if there is a limited number of usages allowed on a particular card, this
  # is to be the number of allowed uses remaining, null if not limited
