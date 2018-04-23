from django.db import models
from django.core.mail import EmailMessage
from twilio.rest import TwilioRestClient
import json
import random
import string
import emails
import os

TWILIO_ACCOUNT_ID = os.getenv('TWILIO_ACCOUNT_ID')
TWILIO_TOKEN = os.getenv('TWILIO_TOKEN')
TWILIO_NUMBER = os.getenv('TWILIO_NUMBER')

class Course(models.Model):
	code = models.CharField(max_length=150)
	title = models.CharField(max_length=500)
	number = models.CharField(max_length=30, primary_key=True)
	
	class Meta:
		ordering = ['code']
	
	def __unicode__(self):
		return self.code + ": " + self.title


class Class(models.Model):
	course = models.ForeignKey(Course)
	number = models.CharField(max_length=30, primary_key=True)
	title = models.CharField(max_length=500)
	time = models.CharField(max_length=30)
	days = models.CharField(max_length=30)
	max = models.IntegerField(default=1000)
	enroll = models.IntegerField(default=0)
	isClosed = models.BooleanField(default=False)
		
	def __unicode__(self):
		return self.course.code + " " + self.title
		
	# for the admin page
	class Meta:
		ordering = ['course', 'title']
		verbose_name_plural = "classes"
		
		
class Entry(models.Model):
	courseNumber = models.CharField(max_length=30)
	section = models.CharField(max_length=30)
	totalEnroll = models.IntegerField(default=0)
	totalClosed = models.BooleanField(default=False)	
	
	
TEXT = 'TEXT'
EMAIL = 'EMAIL'

class Subscription(models.Model):
	theclass = models.ForeignKey(Class)
	address = models.CharField(max_length=100)
	active = models.BooleanField(default=True)
	type = models.CharField(max_length=10)
	
	def sendConfirmation(self):
		if self.type == EMAIL:
			subject = "Your Subscription to %s" % str(self.theclass)
 			body = r"""
You've subscribed to %s via PrincetonPounce!  We'll send you an email if seats in the class open up.
 			""" % str(self.theclass)
  			return emails.sendMail(self.address, subject, body)
  			
  		elif self.type == TEXT:
			sender = TWILIO_NUMBER
			client = TwilioRestClient(TWILIO_ACCOUNT_ID, TWILIO_TOKEN)
			body = r"""
	You've subscribed to %s via PrincetonPounce!  We'll send you a text if seats in the class open up.
			""" % str(self.theclass)
			return client.sms.messages.create(to=self.address, from_=sender, body=body)  			
		
	def sendNotification(self):
		if self.type == EMAIL:
			subject = 'Open Spot in %s' % str(self.theclass)
			body = """A spot has opened up in %s. If the class fills up before you can make it to SCORE, you'll have to resubscribe for notifications here:\n http://pounce.tigerapps.org/reactivate/%s.""" % (str(self.theclass), str(self.pk))
  			return emails.sendMail(self.address, subject, body)

		elif self.type == TEXT:
			sender = TWILIO_NUMBER
			client = TwilioRestClient(TWILIO_ACCOUNT_ID, TWILIO_TOKEN)
			body = """
			A spot has opened up in %s! If you don't make it to SCORE in time, you MUST resubscribe!
			""" % (str(self.theclass))
			try:
				return client.sms.messages.create(to=self.address, from_=sender, body=body)
			except:
				pass
			
	def __unicode__(self):
		return str(self.theclass) + "->" + self.address
		
class CoursesList(models.Model):
	json = models.TextField()
		
	def cache(self):
		courses = []
		for course in Course.objects.all().order_by('code'):
			courseDict = {'courseTitle' : course.title, 'courseId' : course.code, 'courseNumber' : course.number, 'classes' : []}
			pcelink = course.code.split('/')[0].replace(" ", "")
			for theclass in Class.objects.filter(course=course).order_by('title'):
				courseDict['classes'].append({'classTitle' : theclass.title, 'classNumber' : theclass.number, 'classTime' : theclass.time, 'classDays' : theclass.days, 'enroll' : theclass.enroll, 'max' : theclass.max, 'isClosed' : theclass.isClosed, 'pceLink' : pcelink})
			courses.append(courseDict)
		self.json = json.dumps(courses)
		self.save()
