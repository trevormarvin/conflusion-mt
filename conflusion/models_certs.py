#!/usr/bin/env false

# Conflusion Membership Tracker - Member Certification Schema Addendum

'''
This is an addendum file adding to the main "models.py" file adding elements of
the schema necessary for certifications and permissions to access particular
resources.

'''


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
  
  parent = models.ForeignKey(self,
                             null = True,
                             on_delete = models.CASCADE)
  # If this certification is a subset or under another certification, this
  # field is a reference to the parent certification.  If the parent
  # certification lapses or is invalid for a particular user, then this
  # certification should be considered invalid for the user.
  
  comments = models.TextField(null = True)
  # comments about the particular certification
  
  ml_based = models.ForeignKey(Group,
                               null = True)
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
This next logs individual accesses to a certified resource
'''

class CertAccessLog(models.Model):
  index = models.AutoField(primary_key = True)
  
  parent = models.ForeignKey(Certifications,
                             null = True,
                             on_delete = models.CASCADE)
  # the resource that the log entry is for
  
  timestamp = models.DateTimeField(auto_now_add = True)
  # this automatic populating field is the time of the access log event
  
  userid = models.ForeignKey(User,
                             on_delete = models.SET_NULL)
  # this identifies the user that requested the access
  # (We are not relying on the 'certid' field to identify the user, as the user
  # may not be certified and we want to log a failed access attempt.)
  
  certid = models.ForeignKey(Certified,
                             on_delete = models.SET_NULL,
                             null = True)
  # this links back to the certification that allowed the access, null if access
  # was denied
  
  quantity = models.DecimalField(null = True)
  # for particular access logging that aims to record a quantity of something,
  # this field records the quantity of usage to a resource


# --------------------------------
'''
This next table tracks the certifications that a particular user has.
'''

class Certified(models.Model):
  index = models.AutoField(primary_key = True)
  
  userid = models.ForeignKey(User,
                             on_delete = models.CASCADE)
  # the user with the certification
  cert = models.ForeignKey(Certifications,
                           on_delete = models.CASCADE)
  # the certification that the user has
  
  certby = models.ForeignKey(User,
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
  
  
