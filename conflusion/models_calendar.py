#!/usr/bin/env false

# Conflusion Membership Tracker - Event Calendar Schema Addendum

'''
This is an addendum file adding to the main "models.py" file adding elements of
the schema necessary for event scheduling and automatic/dynamic calendar
generation.  This also contains idea for event ticketing.

THIS IS NOT PART OF THE CURRENT BUILD OUT.

'''


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
