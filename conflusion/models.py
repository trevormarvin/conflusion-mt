#!/usr/bin/env false

# Conflusion Membership Tracker

'''
This file essentially provides the schema for the database for the system.

'''

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
  

# ---------------- Sites or Resources -----------------------------------------
'''
Tables listing sites, usually that of locations or facilities, that will have
events scheduled in them.
'''

class Locations(models.Model):
  index = models.AutoField(primary_key = True)
  
  name = models.CharField(max_length = 50,
                          null = False,
                          unique = True)
  # name of the location or resource

  parent = models.ForeignKey('self',
                             null = True,
                             on_delete = models.CASCADE)
  # If the location is a subset or location within another site, this is the
  # reference to the larger entity that contains it.  The primary reason for
  # this relationship is for tracking contention between events that utilize
  # multiple listed locations.  i.e. If an event is scheduled to use a 
  # particular location, then all child locations are assumed to be in use too.

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
  
  parent = models.ForeignKey('self',
                             null = True,
                             on_delete = models.CASCADE)
  # If this certification is a subset or under another certification, this
  # field is a reference to the parent certification.  If the parent
  # certification lapses or is invalid for a particular user, then this
  # certification should be considered invalid for the user.
  
  comments = models.TextField(null = True)
  # comments about the particular certification
  
  logaccess = models.BooleanField(default = False)
  # Whether to log access to the certification for each query.  e.g.  If the
  # certification is access to the front door, then this could specify that
  # a particular user requested (and presumably received) access to unlock the
  # door.  The access request god to another table. ### WHAT TABLE HERE ###
  
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
  
  userid = models.ForeignKey('Users',
                             on_delete = models.CASCADE)
  # the user with the certification
  cert = models.ForeignKey('Certifications',
                           on_delete = models.CASCADE)
  # the certification that the user has
  
  certby = models.ForeignKey('Users',
                             on_delete = models.SET_NULL,
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
    unique_together = ('cert', 'userid', 'certifier')
  

# --------------------------------
'''
This next logs individual accesses to a certified resource
'''

class CertAccessLog(models.Model):
  index = models.AutoField(primary_key = True)
  
  parent = models.ForeignKey('Certifications',
                             null = True,
                             on_delete = models.CASCADE)
  # the resource that the log entry is for
  
  timestamp = models.DateTimeField(auto_now_add = True)
  # this automatic populating field is the time of the access log event
  
  userid = models.ForeignKey('Users',
                             on_delete = models.SET_NULL)
  # this identifies the user that requested the access
  # (We are not relying on the 'certid' field to identify the user, as the user
  # may not be certified and we want to log a failed access attempt.)
  
  certid = models.ForeignKey('Certified',
                             on_delete = models.SET_NULL,
                             null = True)
  # this links back to the certification that allowed the access, null if access
  # was denied
  
  quantity = models.DecimalField(null = True)
  # for particular access logging that aims to record a quantity of something,
  # this field records the quantity of usage to a resource


# --------------------- Tables for Asynchronous Events ------------------------
'''
This next section relates to events that happen that are not tied to particular
accesses to certified resources.  This commonly includes switches tied to doors
or security motion sensors.
'''

class EventItems(models.Model):
  index = models.AutoField(primary_key = True)
  
  eventid = CharField(max_length = 32,
                      unique = True)
  # this will be the short lookup code for the device reporting an event to find
  # the appropriate entry in this table, of which will become the ForeignKey
  # index from the EventAccessLog table
  
  bothedges = BooleanField(default = False)
  # if set, this will instruct that the log should record a device triggering
  # to the asserted state (i.e. a door opening) along with recording the device
  # returning to the unasserted state (i.e. a door closing)
  
  description = CharField(max_length = 128)
  # a description of the sensor or report
  
  logpurgeage = PositiveIntegerField(default = 0)
  # if this value is non-zero, log entries older than this number of days will
  # be automatically deleted during the cleaning and maintainance process
  
  ###### POSSIBLY ADD VALUES HERE ABOUT NOTIFICATIONS TO PARTICULAR USERS THAT
  ###### WILL HAPPEN IF THESE EVENTS HAPPEN OUTSIDE PARTICULAR TIME WINDOWS.
  ###### THIS GOES TOWARDS THE END OF MAKING A FULL SECURITY SYSTEM
  

class EventAccessLog(models.Model):
  index = models.AutoField(primary_key = True)
  
  eventid = ForeignKey('EventItems',
                       on_delete = models.CASCADE)
  # reference to the event that occurred
  
  timestamp = models.DateTimeField(auto_now_add = True)
  # this automatic populating field is the time of event
  
  state = PositiveSmallIntegerField(default = 0)
  # For events that have multiple states that they could be in, this will store
  # that state.  In the case of a door, it would be '1' for opening and '0' for
  # closing.


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
  
  userid = models.ForeignKey('Users',
                             on_delete = models.CASCADE)
  # user that the access card belongs to
  
  suspended = models.BooleanField(default = False)
  # whether the access device is suspended, temporarily or otherwise
  
  expire = models.DateField(null = True)
  # when the access card expires, null if it never expires
  
  countdown = models.PositiveIntegerField(null = True)
  # if there is a limited number of usages allowed on a particular card, this
  # is to be the number of allowed uses remaining, null if not limited
  
  
# ----------------- Tables for Accounting and Payments ------------------------

###### STUFF TO ADD !

# ----------------- Tables for Scheduled Events -------------------------------
'''
These tables relate to scheduled events that may be placed on a public calendar,
may be internal only, or tracking usage of particular resources.
'''

# a calendar for events
class EventCalendar(models.Model):
  index = models.AutoField(primary_key = True)
  
  starttime = models.DateTimeField()
  endtime = models.DateTimeField()
  # start and end time of the event
  
  userid = models.ForeignKey('Users',
                             on_delete = models.SET_NULL,
                             null = True)
  # primary user responsible for the event
  
  location = models.ForeignKey('Locations',
                               on_delete = models.PROTECT,
                               null = True)
  # location resource reserved for the event
  
  description = models.TextField(null = True)
  # description of the event, text to use if on the public website
  
  public = models.BooleanField(default = False)
  # whether to show the event on the public website
  
  price = models.DecimalField()
  # price of the event, per attendee
  
  reserved = models.BooleanField(default = False)
  # whether the event requires reservations, or is essentially ticketed
  # If true, this implies usage of the other tables for tracking such
  
  membersonly = models.BooleanField(default = True)
  # if the event is for members only
  
  certified = models.ForeignKey('Certified',
                                on_delete = models.PROTECT,
                                null = True)
  # if the access to or the ability to register for this event is tied to a
  # certification, reference to the certification
  
  limited = models.PositiveIntegerField(null = True)
  # if there is an attendance limit to the event and 'reserved' is set, this
  # is the limit to the number of tickets

  
# tickets purchased for particular events
class Tickets(models.Model):
  index = models.AutoField(primary_key = True)
  
  event = models.ForeignKey('EventCalendar',
                            on_delete = models.PROTECT)
  # reference to the event
  
  userid = models.ForeignKey('EventCalendar',
                             on_delete = models.PROTECT,
                             null = True)
  # If the attendee is a member of the organization, this is a reference to the
  # members account.
  # In using this field, it is assumed that the user's regular membership access
  # card or device will double for the eTicket to access the event.
  
  guestid = models.CharField(max_length = 128,
                             null = True)
  # If the attendee is not listed in the membership users table, this is a
  # reference to their identity, presumably a legal name that they carry state
  # issued ID for.  If both the 'userid' and 'guestid' field are populated, then
  # the 'guestid' is presumed to be a guest of the user who is listed.
  
  seat = models.CharField(max_length = 16,
                          null = True)
  # If there is assigned seating to the event, this is the reference to the
  # assigned seat.  When seats for guests are assumed to be selected such that
  # they are sequential or in proximity to each other, they should all contain
  # the same 'userid'.  Unless otherwise handled, this will be the method for
  # identifying groups when seat assignments need to be changed.
  
  regtime = models.DateTimeField(auto_now = True)
  # when the ticket registration/reservation was made
  
  eticketid = models.CharField(max_length = 128,
                               null = True,
                               unique = True)
  # unique identifier for an electronic ticket, if the user access member is
  # not utilized
  
  arrived = models.DateTimeField(null = True)
  entrance = models.CharField(max_length = 32,
                               null = True)
  # set when a ticket/reservation has been redeemed
  
  # Multiple duplicated entries may exist in the event that a user purchases
  # multiple tickets to an event.