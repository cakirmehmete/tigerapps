from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from utils.dsml import gdi
from django.contrib.auth.decorators import login_required, user_passes_test
from models import *
from views import get_user
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django import forms
import json
import sys,os
import traceback
import simplejson

from real_time_avail import start_sim, stop_sim, check_avail
from real_time_queue import check, edit


def json_response(value, **kwargs):
    """Return JSON-encoded value in an HttpResponse."""
#    kwargs.setdefault('content_type', 'text/javascript; charset=UTF-8')
    response =  HttpResponse(simplejson.dumps(value), **kwargs)
    response['Access-Control-Allow-Methods'] =  "JSON"
    return response
    
@login_required
def update_queue(request, drawid):
    user = get_user(request.user.username)
    if not user:
        return HttpResponse('forbidden')
    draw = Draw.objects.get(pk=drawid)
    qlist = json.loads(request.POST['queue'])
    queue = user.queues.filter(draw=draw)[0]
    if not queue:
        return HttpResponse('no queue')
    try:
        return json_response(edit(user, queue.id, qlist, draw))
    except Exception as e:
        return HttpResponse(e)

# Ajax for displaying this user's queue
@login_required
def get_queue(request, drawid, last_version = 0):
    user = get_user(request.user.username)
    last_version = int(last_version)
    if not user:
        return HttpResponse('no user')
    try:
        draw = Draw.objects.get(pk=drawid)
        queue = user.queues.get(draw=draw)
    except Exception as e:
        return HttpResponse(traceback.format_exc(2) + str(draw))
    try:
        return json_response(check(user, queue.id, last_version))
    except Exception as e:
        return HttpResponse(traceback.format_exc(2))
    
def start_simulation(request, delay, size=1):
    delay = int(delay)
    size = int(size)
    return start_sim(delay, size)

def stop_simulation(request):
    return stop_sim()

def check_availability(request, timestamp):
    return json_response(check_avail(int(timestamp)))
