# Resets Pounce for a new semester.

# HEY: YOU MUST ALSO KILL -9 THE CURRENTLY RUNNING
# UPDATE PROCESSES!

import sys,os
sys.path.insert(0,os.path.abspath("/srv/tigerapps"))
import settings
from django.core.management import setup_environ
setup_environ(settings)

from pounce.models import *

Subscription.objects.all().delete()
Class.objects.all().delete()
Course.objects.all().delete()
Entry.objects.all().delete()
	
CoursesList.objects.all()[0].delete()
