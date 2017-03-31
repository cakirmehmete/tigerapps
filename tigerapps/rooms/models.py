from django.db import models
from django.forms import ModelForm
import time

# New stuff for the disclaimer tracking
class Disclaimer(models.Model):
    netid = models.CharField(max_length=30, db_index=True)
    date = models.DateTimeField(db_index=True)

# A new room review object
class NewReview(models.Model):
    netid = models.CharField(max_length=30, db_index=True)
    building_id = models.CharField(max_length=10, db_index=True)
    room_number = models.CharField(max_length=10, db_index=True)
    date = models.DateField(auto_now_add=True)
    RATINGS = ( (i, i) for i in range(1, 6) )
    rating = models.IntegerField(choices=RATINGS)
    summary = models.CharField(max_length=80)
    content = models.TextField("Review")

    YEAR_IN_SCHOOL_CHOICES = (
        ("Freshman", 'Freshman'),
        ("Sophomore", 'Sophomore'),
        ("Junior", 'Junior'),
        ("Senior", 'Senior'),
    )
    class_year = models.CharField("Class Year",
        max_length=10,
        choices=YEAR_IN_SCHOOL_CHOICES,
        blank=True,
        help_text="What year did you live in this room?"
    )
    draw_time = models.CharField("Draw Time", max_length=80, blank=True,
                help_text="How good was your draw time?")

    def __unicode__(self):
        return self.summary


# keeping this old stuff in to not mess with database

photopath = 'photo'

class Draw(models.Model):
    name = models.CharField(max_length=24)

    def __unicode__(self):
        return self.name

# campus buildings
class Building(models.Model):
    name = models.CharField(max_length=30)
    pdfname = models.CharField(max_length=30)
    availname = models.CharField(max_length=30)
    draw = models.ManyToManyField('Draw')
    lat = models.FloatField()
    lon = models.FloatField()

    def __unicode__(self):
        return self.name

# door rooms
class Room(models.Model):

    GENDER_CHOICES = (
        ('E', 'Either'),
        ('M', 'Male'),
        ('F', 'Female'),
        ('X', 'Mixed')
	)

    BATHROOM_CHOICES = (
        ('PU', 'Public'),
        ('PR', 'Private'),
        ('SH', 'Shared')
	)

    RATINGS = ( (i, i) for i in range(6) )

	# room numbers can include letters
    number = models.CharField(max_length=10)
    sqft = models.IntegerField()
    occ = models.IntegerField()
    building = models.ForeignKey('Building')
    subfree = models.BooleanField()
    numrooms = models.IntegerField()
    floor = models.IntegerField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    avail = models.BooleanField()
    adjacent = models.CharField(max_length=10)
    # ADA accessible
    ada = models.BooleanField()
    # bi-level room
    bi = models.BooleanField();
    # connecting single
    con = models.BooleanField();
    bathroom = models.CharField(max_length=2, choices=BATHROOM_CHOICES)
    # When this entry was updated
    updated = models.DateField()
    # Whether this is currently an undergrad room.
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return "%s %s" % (self.building.name, self.number)

# users
class User(models.Model):
    netid = models.CharField(max_length=30)
    firstname = models.CharField('First Name', max_length=45, null=True, blank=True) # givenName
    lastname = models.CharField('Last Name', max_length=45, null=True, blank=True) # sn
    pustatus = models.CharField(max_length=20, null=True, blank=True) # undergraduate or graduate
    puclassyear = models.IntegerField('Class Year', null=True, blank=True) # puclassyear
    queues = models.ManyToManyField('Queue')
    do_email = models.BooleanField(default=True)
    phone = models.CharField(max_length=12, blank=True)
    do_text = models.BooleanField(default=False)
    carrier = models.ForeignKey('Carrier', null=True, blank=True)
    confirmed = models.BooleanField('Confirmed', default=False) #whether or not has confirmed phone number
    seen_welcome = models.BooleanField(default=False)

    def __unicode__(self):
        return self.netid

# queues
class Queue(models.Model):
    EDIT = 0
    JOIN = 1
    CREATE = 2
    UPDATE_KINDS = (
        (EDIT, 'EDIT'),
        (JOIN, 'JOIN'),
        (CREATE, 'CREATE'),
        )

    draw = models.ForeignKey('Draw')
    # Last update information.
    # The version number of this queue (how many updates has it had?).
    version = models.IntegerField(default=1)
    # Edit, merge or create.
    update_kind = models.IntegerField(choices=UPDATE_KINDS, default=CREATE)
    # Editing or joining user. Create: None.
    update_user = models.ForeignKey('User', null=True, default=None)

    def __unicode__(self):
        return self.draw.name

# queue-to-room mappings
class QueueToRoom(models.Model):
    queue = models.ForeignKey('Queue')
    room = models.ForeignKey('Room')
    ranking = models.IntegerField()

# An invitation to a the queue owned by a user
class QueueInvite(models.Model):
    sender = models.ForeignKey('User', related_name='q_sent_set')
    receiver = models.ForeignKey('User', related_name='q_received_set')
    draw = models.ForeignKey('Draw')
    # UNIX timestamp
    timestamp = models.IntegerField()

    def __unicode__(self):
        return "%s->%s %s" % (self.sender.netid, self.receiver.netid, self.draw.name)

    def accept(self):
        q1 = self.sender.queues.get(draw=self.draw)
        q2 = self.receiver.queues.get(draw=self.draw)
        # Check whether queues are same.
        if q1.id == q2.id:
            self.delete()
            return None
        # Delete the old queue if no users are left with it.
        deleting = False
        if len(q2.user_set.all()) == 1:
            deleting = True
        # Merge the receiver's queue contents into the sender's.
        rooms1 = set([qtr.room for qtr in q1.queuetoroom_set.all()])
        qtrs2 = q2.queuetoroom_set.all()
        ranking = len(rooms1)
        for qtr in qtrs2:
            if qtr.room in rooms1:
                continue
            qtr.ranking = ranking
            qtr.queue = q1
            # Create a new DB row if old qtr entry still needed.
            if not deleting:
                qtr.pk = None
            qtr.save()
            rooms1.add(qtr.room)
            ranking += 1
        # Leave old queue, delete it if possible.
        self.receiver.queues.remove(q2)
        if deleting:
            q2.delete()
        # Join new queue, and update its version data.
        self.receiver.queues.add(q1)
        q1.version += 1
        q1.update_kind = Queue.JOIN
        q1.update_user = self.receiver
        q1.save()
        # Remove this invitation.
        self.delete()
        return q1

    def deny(self):
        self.delete()

# room review
class Review(models.Model):

    RATINGS = ( (i, i) for i in range(6) )

    room = models.ForeignKey('Room')
    summary = models.CharField(max_length=80)
    date = models.DateField(auto_now_add=True)
    content = models.TextField()
    rating = models.IntegerField(choices=RATINGS)
    user = models.ForeignKey('User')

    def __unicode__(self):
        return self.summary

class ReviewForm(ModelForm):
    class Meta:
        model = Review
        exclude = ('user', 'room')

class Photo(models.Model):

    date = models.DateField(auto_now_add=True)
    photo = models.ImageField(upload_to=photopath)

    def __unicode__(self):
        return "Photo on %s" % (self.date)

# Information (size, timeframe, etc) about a past draw
class PastDraw(models.Model):
    draw = models.ForeignKey('Draw')
    year = models.IntegerField()
    # The number of rooms that drew in this draw
    numrooms = models.IntegerField()
    # The number of people that drew in this draw
    numpeople = models.IntegerField()

    def __unicode__(self):
        return "%s %d" % (self.draw.name, self.year)

# A past draw entry
class PastDrawEntry(models.Model):
    pastdraw = models.ForeignKey('PastDraw')
    room = models.ForeignKey('Room')
    # A UNIX timestamp for the time room was selected
    timestamp = models.IntegerField()
    # The number of *rooms* that drew in this draw before this room
    roomrank = models.IntegerField()
    # The number of *people* who drew in this draw before this room
    peoplerank = models.IntegerField()

    def __unicode__(self):
        return "%s %s %d" % (self.room.number, self.room.building.name,
                             self.pastdraw.year)

# A phone carrier, used for text notifications
class Carrier(models.Model):
    #email-to-text address
    name = models.CharField(max_length=30)
    address = models.CharField(max_length=30)
    def __unicode__(self):
        return self.name
