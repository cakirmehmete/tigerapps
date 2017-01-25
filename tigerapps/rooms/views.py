import re
from functools import wraps
from django.conf import settings as conf
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.views.decorators.cache import cache_control, cache_page
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.gzip import gzip_page
from django.template import RequestContext
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django import forms
import json
import traceback
from utils.dsml import gdi
#from models import *

cache_bust='?bust=v3'

def index(request):
	if 'facebookexternalhit' in request.META['HTTP_USER_AGENT'].lower() or 'facebot' in request.META['HTTP_USER_AGENT'].lower():
		return render_to_response('newrooms/fbmarkup.html', {'bust': cache_bust})
	return HttpResponseRedirect(reverse('rooms.views.map'))

@login_required
def map(request):
    return render_to_response('newrooms/map.html', {'username': request.user.username,
    	'bust':  cache_bust})

@login_required
def table(request):
    return render_to_response('newrooms/table.html', {'username': request.user.username,
    	'bust': cache_bust})
