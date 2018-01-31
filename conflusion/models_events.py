#!/usr/bin/env false

# Conflusion Membership Tracker - Logged Events Schema Addendum

'''
This is an addendum file adding to the main "models.py" file adding elements of
the schema necessary for logging asynchronous events like security sensor data.

THIS IS NOT PART OF THE CURRENT BUILD OUT.

'''


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

