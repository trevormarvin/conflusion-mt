#!/usr/bin/env false

# Conflusion Membership Tracker - Locations Schema Addendum

'''
This is an addendum file adding to the main "models.py" file adding elements of
the schema necessary for location scheduling.

THIS IS NOT PART OF THE CURRENT BUILD OUT.

'''


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

