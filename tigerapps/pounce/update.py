import sys,os
sys.path.insert(0,os.path.abspath("/srv/tigerapps"))
import settings
from django.core.management import setup_environ
setup_environ(settings)

from pounce.models import Course, Class, Subscription, Entry, CoursesList
import pounce.log as log
import urllib2
from bs4 import BeautifulSoup
import twitter

TERM = '1174'

def updateCourse(course):
	log.log("Updating %s" % str(course))

 	url = "https://registrar.princeton.edu/course-offerings/course_details.xml?courseid={}&term={}".format(course.number, TERM)
	html = urllib2.urlopen(url).read()
	soup = BeautifulSoup(html)

	rows = soup.find_all('tr')[1:]
	for row in rows:
			fields = row.find_all('td')

			classNumber = fields[0].get_text().strip()
			if not classNumber:
				continue

			theclass, created = Class.objects.get_or_create(number=classNumber, course=course)
			theclass.title = fields[1].get_text().strip()
			theclass.time = fields[2].get_text().strip().replace("\n", "")
			theclass.days = fields[3].get_text().strip().replace("\n", "")
			raw = fields[5].get_text().replace("\n","").replace(" ","")
			sindex = raw.find("Enrolled:")
			eindex = raw.find("Limit:")
			theclass.enroll = int(raw[sindex+9:eindex])
			theclass.max = int(raw[eindex+6:] or 1000)

			isClosed = fields[6].get_text().strip() == "Closed"
			if not isClosed:
				freeSpots = theclass.max - theclass.enroll
				try:
					# don't tweet "P99"
					if theclass.title != "P99":
						twitter.tweet("%s has %d open spot(s)." % (str(theclass), freeSpots))
 				except Exception:
 					pass
				log.log("Class %s is now open!" % str(classNumber))
				for subscription in Subscription.objects.filter(theclass=theclass, active=True):
					log.log("Sending subscription %s." % str(subscription))
					subscription.sendNotification()
					subscription.active = False
					subscription.save()

			theclass.isClosed = isClosed

			theclass.save()

# Check for duplicates.  For some reason, this is necessary.
def clean():
	def contains(list, entry):
		for e in list:
			if entry.courseNumber == e.courseNumber and entry.section == e.section:
				return True
		return False

	entries = Entry.objects.all()
	past = []
	for entry in entries:
		if contains(past, entry):
			print "Deleting", entry.courseNumber, entry.section
			entry.delete()
		else:
			past.append(entry)

