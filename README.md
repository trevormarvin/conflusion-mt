## Conflusion Membership Tracker

The "Conflusion" program aims to be a membership tracking and resource management system for makerspaces and similar organizations.

This project is an invention whose mother will be the necessities of the Confluent makerspace in Richland, WA (USA).  It is also driven by the acquisition of point-of-sale equipment and other gizmos.

One of the visions is to build a membership tracking system that utilizes a point-of-sale terminal and card reader, tracks memberships and authorizations for access to certain tools in the makerspace, and may handle purchases and subscription payments to the makerspace.

Management features should be built to be accessible from a webpage interface, thus making it platform agnostic.  Software built for use on kiosk and point-of-sale equipment will be designed to run on Linux systems.

This repository is put together using Pipenv and Virtual Environments.  See this to help get you started is you're not familiar with it:  http://docs.python-guide.org/en/latest/dev/virtualenvs/

The 2.x version of Django is being used here, so that ends up requiring version 3 Python.  Sub modules may be written in other languages and versions of Django and Python, but the core is Django 2.x and Python 3.
