from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.template import RequestContext
from pom.models import *
import datetime
import simplejson

def index(request, offset):
    # not used due to direct_to_template in urls.py
    return render_to_response('pom/index.html', {}, RequestContext(context))

def map_bldg_clicked(request, bldg_code):
    try:
        bldg = Building.objects.get(bldg_code=bldg_code)
        bldg_name = bldg.name
        events = Building.cal_events.all(bldg)
        response_json = simplejson.dumps({'bldgName': bldg_name,
                                          'events': [event.event_cluster.cluster_title for event in events],
                                          'error': False})
    except Exception, e:
        response_json = simplejson.dumps({'bldgName': str(e)})
        
    
    return HttpResponse(response_json, content_type="application/javascript")
