import collections
from django.db import models
import ast
from wintersession.time_decode import decode_time
from blocks import blocks_to_friendly, friendly_to_blocks
import re


class BlocksField(models.TextField):
    __metaclass__ = models.SubfieldBase
    description = "Stores a python list"

    def __init__(self, *args, **kwargs):
        super(BlocksField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value:
            value = []

        if isinstance(value, list):
            return value

        #A bit of a hack to give friendlier schedule views in admin
        #Check for a friendly formatted string and convert back
        #See also the BlocksWidget in admin.py
        if not re.match('\[(\s*\d{4}\s*|,)*\]', value):
            return friendly_to_blocks(value)

        return [int(x) for x in value.replace("[", "").replace("]", "").replace(" ", "").split(",")]

    def get_prep_value(self, value):
        if value is None:
            return value
        #A bit of a hack to give friendlier schedule views in admin.
        return str(value)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_prep_value(value)

class Student(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    netID = models.CharField(max_length=16, unique=True)
    agenda_visibility = models.BooleanField(default=False)

    def blocks(self):
        blks = []
        for course in self.course_set.all():
            for blk in course.blocks:
                blks.append(blk)
        return blks

    def isScheduleConsistent(self):
        blks = self.blocks()
        return len(blks) == len(set(blks))

    def whyScheduleInconsistent(self):
    # Returns a tuple of conflicting courses, if any
    # Does not identify more than one conflict at a time
        if self.isScheduleConsistent():
            return
        for course1 in self.course_set.all():
            for course2 in self.course_set.all():
                if course1 == course2:
                    break
                for block2 in course2.blocks:
                    if block2 in course1.blocks:
                        return (course1, course2)
        raise RuntimeException('Should have found conflicting courses.')

    def __unicode__(self):  # Python 3: def __str__(self):
        return self.netID

class Instructor(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    netID = models.CharField(max_length=16, unique=True)
    faculty = models.BooleanField(default=False)

    def __unicode__(self):  # Python 3: def __str__(self):
        return self.netID

    def billable(self):
        if self.faculty:
            return 0
        my_courses = self.course_set.all()
        hours = 0.0
        for course in my_courses:
            hours += len(course.blocks)/2.0
        return hours

    def full_name(self):
        return self.first_name+" "+self.last_name

class Course(models.Model):
    courseID = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=150,default='Title needed')
    description = models.TextField(max_length=1000)
    other_section = models.ManyToManyField('self', blank=True, symmetrical=True)
    min_enroll = models.IntegerField(default=0)
    max_enroll = models.IntegerField(default=200)
    cancelled = models.BooleanField(default=False)
    room = models.CharField(max_length=200,default='tbd')
    blocks = BlocksField('Course blocks')
    schedule = models.CharField(max_length=50)
    students = models.ManyToManyField(Student, through='Registration')
    instructors = models.ManyToManyField(Instructor)

    class Meta:
        ordering = ['title']

    def __unicode__(self):  # Python 3: def __str__(self):
        return self.courseID + ' ' + self.title

    def current_enroll(self):
        return len(self.students.all())

    def current_enroll_exclude(self, **kwargs):
        return len(self.students.exclude(**kwargs))

    # Hack to allow 30% over-registration
    def max_enroll_with_extra(self):
        # Hack to override with exact amounts
        if self.courseID[0] == 'E':
            return self.max_enroll
        return int(1.3 * self.max_enroll)

    def is_full(self):
        num_enroll = self.current_enroll()
        return num_enroll >= self.max_enroll_with_extra()

    def meets_min_requirements(self):
        num_enroll = self.current_enroll()
        return num_enroll >= self.min_enroll

    def get_instructors(self):
        return ", ".join([i.full_name() for i in self.instructors.all()])

    def this_section(self):
        return Section(self.blocks)

    def all_section_ids(self):
        section_ids = [self.id]
        for section in self.other_section.all():
            section_ids.append(section.id)
        return section_ids

    def all_sections(self):
        sections = [Section(self.blocks)]
        if self.other_section:
            for section in self.other_section.all():
                sections.append(Section(section.blocks))
        return sections

    is_full.boolean = True
    meets_min_requirements.boolean = True

class Section:
    def __init__(self, blocks):
        self.blocks = blocks

    def as_dict(self, human_readable=False):
        agend = {}
        for i in range(0, 7):
            agend[i] = []

        # If temporary list, return empty dict
        if self.blocks == [0]:
            return agend

        # We're going to make a dict with seven entries. Values will be dicts for
        # each day of the week. the subdicts will map start timecodes to tuples
        # with format (start time, end time)
        prev_blk = start_blk = self.blocks[0]
        # for each block in that course
        for n in xrange(1, len(self.blocks) + 1):
            # if block continues from previous, or past last block
            if n == len(self.blocks) or self.blocks[n] != prev_blk + 5:
                # record the previous session
                dow = start_blk / 1000
                if human_readable:
                    start_time = decode_time(start_blk % 1000)
                    end_time = decode_time((prev_blk + 5) % 1000)
                else:
                    start_time = (start_blk / 10.0) % 100
                    end_time = ((prev_blk + 5) / 10.0) % 100
                info = (start_time, end_time)
                agend[dow].append(info)

                # and start a new one
                if n != len(self.blocks):
                    start_blk = prev_blk = self.blocks[n]
            else:
                prev_blk = self.blocks[n]

        return agend

    def as_string(self):
        dow = {0: "Su", 1: "M", 2: "Tu", 3: "W", 4: "Th", 5: "F", 6: "Sa"}
        # First group all sessions by time (start and end)
        times = {}
        for day, day_sessions in self.as_dict(human_readable=True).iteritems():
            for session_tuple in day_sessions:
                session_string = str(session_tuple[0]) + "-" + str(session_tuple[1])
                if session_string not in times:
                    times[session_string] = []
                times[session_string].append(dow[day])
        # Build string
        times_grouped = []
        for time, days in times.iteritems():
            times_grouped.append("/".join(days) + " " + time)
        return ", ".join(times_grouped)

class Registration(models.Model):
    student = models.ForeignKey(Student)
    course = models.ForeignKey(Course)
    timestamp = models.DateTimeField('Registration timestamp',auto_now_add=True)

    attendance_M = models.BooleanField(default=False)
    attendance_Tu = models.BooleanField(default=False)
    attendance_W = models.BooleanField(default=False)
    attendance_Th = models.BooleanField(default=False)
    attendance_F = models.BooleanField(default=False)

    def __unicode__(self):  # Python 3: def __str__(self):
        return self.student.netID+"-"+self.course.courseID
