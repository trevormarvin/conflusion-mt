#!/usr/bin/env python3

'''
This file is part of the Conflusion-MT suite

This file is intended to be launched by iNetD, but can be run as a server if
given an argument of the port to bind to.

FIRST PASS AT CODE, NOT EVEN READY FOR TESTING, PUSHED AS PART OF BACKUP

'''

import argparse, time, sys, os, time, socket, select, http.server

# -----------------------------------------------------------------------------
class handle_request(http.server.BaseHTTPRequestHandler):
  
  def do_GET(self):
    print("GET: REQUEST PATH: " + self.path)
    
    self.params = {}
    
    if '?' in self.path:
      for param in self.path.split('?', 1)[1].split(','):
        if '=' in param:
          var, val = param.split('=', 1)
          self.params[var] = val
    
    return self.response()
  
  
  def do_POST(self):
    print("POST: REQUEST PATH: " + self.path)
    
    self.params = {}
    
    postdata = self.rfile.read(int(self.headers['Content-Length']))
    for line in postdata.readlines():
      print(line) ##################
      ###### GET POST REQUEST VARS INTO self.params ######
    
    return self.response()
  
  
  def response(self):
    
    #print("HEADERS DIR: " + str(dir(self.headers)))
    for header in self.headers:
      #print("HEADERS: " + str(header) + ' ' + str(self.headers[header]))
      self.params[header] = self.headers[header]
    
    if not "Device-ID" in self.params:
      self.send_response(400)
      self.send_header('Content-type', 'text/html')
      self.end_headers()
      self.wfile.write(bytes('"Device-ID" is missing', 'utf8'))
      return
    
    if not "Card-ID" in self.params:
      self.send_response(400)
      self.send_header('Content-type', 'text/html')
      self.end_headers()
      self.wfile.write(bytes('"Card-ID" is missing', 'utf8'))
      return
    
    try:
      certdobj = models.Certifications.objects.get(code = self.params['Device-ID'])
    except ObjectDoesNotExist:
      self.send_response(400)
      self.send_header('Content-type', 'text/html')
      self.end_headers()
      self.wfile.write(bytes('Device-ID missing from DB', 'utf8'))
      return
    
    try:
      carddobj = models.AccessCards.objects.get(cardid = self.params['Card-ID'])
    except ObjectDoesNotExist:
      self.send_response(400)
      self.send_header('Content-type', 'text/html')
      self.end_headers()
      self.wfile.write(bytes('"Card-ID" does not exist in DB', 'utf8'))
      if certdobj.logaccess and certdobj.logfailed:
        logdobj = models.CertAccessLog()
        logdobj.resource = certdobj
        logdobj.failed = True
        ###### MAYBE CREATE A FIELD TO SAVE CARD ID?
        logdobj.save()
      ###### MAYBE LOG AN INVALID CARD?
      return
    
    try:
      userdobj = models.User.objects.get(index = carddobj.userid)
    except ObjectDoesNotExist:
      self.send_response(400)
      self.send_header('Content-type', 'text/html')
      self.end_headers()
      self.wfile.write(bytes('User missing from DB, should not happen!', 'utf8'))
      return
    
    if carddobj.suspended:
      self.send_response(400)
      self.send_header('Content-type', 'text/html')
      self.end_headers()
      self.wfile.write(bytes('Card is suspended', 'utf8'))
      if certdobj.logaccess and certdobj.logfailed:
        logdobj = models.CertAccessLog()
        logdobj.resource = certdobj
        logdobj.userid = userdobj
        logdobj.failed = True
        logdobj.save()
      return
    
    if carddobj.expire:
      pass
      ###### COMPARE DATE TO CHECK EXPIRED CARD
    
    if not carddobj.countdown is None:
      if carddobj.countdown == 0:
        self.send_response(400)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(bytes('Card is exhausted', 'utf8'))
        if certdobj.logaccess and certdobj.logfailed:
          logdobj = models.CertAccessLog()
          logdobj.resource = certdobj
          logdobj.userid = userdobj
          logdobj.failed = True
          logdobj.save()
        return
        
    if userdobj.expire:
      pass
      ###### COMPARE DATE TO CHECK EXPIRED USER
      
    try:
      certeddobj = models.Certified.objects.get(userid = carddobj.userid,
                                                cert = certdobj.index)
    except ObjectDoesNotExist:
      certeddobj = None
      # not explicitly certified
      if certdobj.ml_based:
        pass
        ###### MEMBERSHIP LEVEL BASED PERMISSIONS, CHECK IF ACCEPTED
      
      self.send_response(400)
      self.send_header('Content-type', 'text/html')
      self.end_headers()
      self.wfile.write(bytes('no certification for user', 'utf8'))
      return
    
    else:  # fall thru to here if explicit certification exists,
      # but not if a DB entry doesn't exist but it's allowed by membership level
      if certeddobj.suspended:
        self.send_response(400)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(bytes("user's certification is suspended", 'utf8'))
        if certdobj.logaccess and certdobj.logfailed:
          logdobj = models.CertAccessLog()
          logdobj.resource = certdobj
          logdobj.userid = userdobj
          logdobj.certid = certeddobj
          logdobj.failed = True
          logdobj.save()
        return
        
      if certeddobj.expire:
        pass
        ###### CHECK FOR EXPIRED CERTIFICATION
        if False:
          self.send_response(400)
          self.send_header('Content-type', 'text/html')
          self.end_headers()
          self.wfile.write(bytes("user's certification is expired", 'utf8'))
          if certdobj.logaccess and certdobj.logfailed:
            logdobj = models.CertAccessLog()
            logdobj.resource = certdobj
            logdobj.userid = userdobj
            logdobj.certid = certeddobj
            logdobj.failed = True
            logdobj.save()
          return
        
    # count down for limited use cards
    if not carddobj.countdown is None:
      carddobj.countdown -= 0
      carddobj.save()
    
    # log the access
    if certdobj.logaccess:
      logdobj = models.CertAccessLog()
      logdobj.resource = certdobj
      logdobj.userid = userdobj
      if certeddobj:
        logdobj.certid = certeddobj
      if 'quantity' in self.params:
        try:
          value = float(self.params['quantity'])
        except:
          pass
        else:
          logdobj.quantity = value
      logdobj.save()
    
    self.send_response(200)
    self.send_header('Content-type', 'text/html')
    self.end_headers()
    self.wfile.write(bytes('Open says me!', 'utf8'))
    return
    
  
# ------------------------------------------------------
# command line option parsing

parser = argparse.ArgumentParser()
parser.add_argument("-v", dest='debug', \
                    action="count", default=0, \
                    help="debug vebosity")
parser.add_argument("-D", dest='daemon', type = str, \
                    help="connect to and listen to a particular port")
args = parser.parse_args()

debug = args.debug

# -------------------------------------------------------------
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "conflusion.settings")
from conflusion import models
from django.core.exceptions import ObjectDoesNotExist
import django
django.setup()

'''
From the source code of http.server, the class expects to receive:
"class BaseHTTPRequestHandler(socketserver.StreamRequestHandler):"

This is a ref to the documentation of what it expects to see:
https://docs.python.org/3/library/socketserver.html#socketserver.StreamRequestHandler
which is a sub class of this:
https://docs.python.org/3/library/socketserver.html#socketserver.BaseRequestHandler



'''
if not args.daemon:
  ###### THIS SECTION NEEDS A LOT OF WORK
  ###### NEED TO SHOVE STDIN/STDOUT INTO THE COMM SOCKET OF THE SERVER FUNCTION
  # assume being launched from iNetD
  import socketserver
  class pseudosocketclass(socketserver.StreamRequestHandler):
    
    def rfile(self, length):
      sys.stdin.read(length)
      
    def wfile(self, data):
      sys.stdout.write(data)
  
  pseudosocket = pseudosocketclass()
  
  handle_request(pseudosocket)
  
  '''
  # this is a snippet of code that with turn stdin/stdout into a TCP socket class
  # convert the stdin/out to a TCP socket
  tcpsock = socket.fromfd(sys.stdin.fileno(), socket.AF_INET, socket.SOCK_STREAM)
  handle_request(request,
                 tcpsock.getpeername(),
                 server,
                 close_connection = True)
  '''
  sys.exit(0)
                 
else:
  # launch a server to answer requests
  if not ':' in args.daemon:
    address = ''
    port = int(args.daemon)
  else:
    address = args.daemon.split()[0]
    port = int(args.daemon.split()[1])
    
  httpd = http.server.HTTPServer((address, port), handle_request)
  httpd.serve_forever()

    