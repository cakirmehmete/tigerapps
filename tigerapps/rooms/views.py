from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.forms import ModelForm, Select, Textarea, TextInput
from django.utils.translation import ugettext_lazy

from models import Disclaimer, NewReview
from datetime import datetime, timedelta

#from utils.dsml import gdi
#from models import *

cache_bust='?bust=v7'

validation_text = "I understand this website is not an official source of rooms data"

def index(request):
	if 'facebookexternalhit' in request.META['HTTP_USER_AGENT'].lower() or 'facebot' in request.META['HTTP_USER_AGENT'].lower():
		return render_to_response('newrooms/fbmarkup.html', {'bust': cache_bust})
	return HttpResponseRedirect(reverse('rooms.views.map'))

@login_required
def map(request):
	disclaimer_expiration = datetime.now() - timedelta(weeks=50) #About 1 year ago
	filled_disclaimer = Disclaimer.objects.filter(netid=request.user.username, date__gte=disclaimer_expiration).exists()
	return render_to_response('newrooms/map.html',
		{'username': request.user.username, 'bust':  cache_bust, 'validation_text': validation_text,
		'filled_disclaimer': str(filled_disclaimer).lower()},
		context_instance=RequestContext(request))

@login_required
def table(request):
	disclaimer_expiration = datetime.now() - timedelta(weeks=50) #About 1 year ago
	filled_disclaimer = Disclaimer.objects.filter(netid=request.user.username, date__gte=disclaimer_expiration).exists()
	left_review = NewReview.objects.filter(netid=request.user.username, date__gte=disclaimer_expiration).exists()
	return render_to_response('newrooms/table.html', {'username': request.user.username, 'bust':  cache_bust, 'validation_text': validation_text,
				'filled_disclaimer': str(filled_disclaimer).lower(), 'left_review': left_review},
				context_instance=RequestContext(request))

@login_required
def disclaimer(request):
	def equal_ignore_punctuation(str1, str2):
		return [c for c in str1.lower() if c.isalpha()] == [c for c in str2.lower() if c.isalpha()]

	if request.method == "POST":
		if equal_ignore_punctuation(validation_text, request.POST['text']):
			d = Disclaimer(netid=request.user.username, date=datetime.now())
			d.save()
			print "Text Matched!!"

		return HttpResponseRedirect(request.POST['redirect'])
	else:
		return HttpResponseRedirect('rooms.views.map')

@login_required
def view_reviews(request, building, room):
	reviews_list = NewReview.objects.filter(building_id=building, room_number=room).order_by('-date')
	try:
		NewReview.objects.get(netid=request.user.username, building_id=building, room_number=room)
		madeReview=True
	except NewReview.DoesNotExist:
		madeReview=False

	paginator = Paginator(reviews_list, 7)

	page = request.GET.get('page')
	if page == None:
		page = 1
	try:
		reviews = paginator.page(page)
	except PageNotAnInteger:
		# If page is not an integer, deliver first page.
		reviews = paginator.page(1)
	except EmptyPage:
		# If page is out of range (e.g. 9999), deliver last page of results.
		reviews = paginator.page(paginator.num_pages)

	return render_to_response('newrooms/view_reviews.html',
					{'room': room, 'building': building, 'reviews':reviews, 'madeReview': madeReview,
					'path': request.get_full_path()})


class NewReviewForm(ModelForm):
	class Meta:
		model = NewReview
		fields = ['rating', 'summary', 'content', 'class_year', 'draw_time']
		widgets = {
			'rating': Select(attrs={'class':'form-control stars'}),
			'summary': TextInput(attrs={'class':'form-control'}),
			'content': Textarea(attrs={'class':'form-control', 'rows':4}),
			'class_year': Select(attrs={'class':'form-control'}),
			'draw_time': TextInput(attrs={'class':'form-control'})
		}

@login_required
def add_review(request, building, room):
	try:
		review = NewReview.objects.get(netid=request.user.username, building_id=building, room_number=room)
		editing=True
	except NewReview.DoesNotExist:
		review = None
		editing=False

	if request.method == "POST":
		form = NewReviewForm(request.POST, instance=review)
		if form.is_valid():
			review = form.save(commit=False)
			review.room_number = room
			review.building_id = building
			review.netid = request.user.username
			if request.POST['action'] == 'delete':
				review.delete()
				return HttpResponseRedirect(reverse('rooms.views.view_reviews', kwargs={'building':building,'room':room}))
			elif not review.pk and NewReview.objects.filter(netid=request.user.username).count() >= 6:
				#Limit people to leaving 6 total reviews
				#This needs to be changed in newer django versions, using form.add_error()
				form._errors["__all__"] = form.error_class(["You have already written too many reviews. Please only leave reviews on rooms you have lived in. Delete an earlier review before adding more"])
			else:
				review.save()
				return HttpResponseRedirect(reverse('rooms.views.view_reviews', kwargs={'building':building,'room':room}))

	else:
		form = NewReviewForm(instance=review)

	return render_to_response('newrooms/add_review.html',
								{'form': form, 'editing': editing, 'path': request.get_full_path()},
								context_instance=RequestContext(request))
