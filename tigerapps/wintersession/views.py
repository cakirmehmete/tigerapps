#from django.http import HttpResponse
from django.core.context_processors import csrf
from django.core.mail import send_mass_mail, EmailMessage
from django.http import HttpResponseRedirect
from django.template import RequestContext, loader
from django.shortcuts import render, render_to_response, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST, require_GET
from wintersession.models import Course, Student, Registration, Instructor
from django_tables2 import RequestConfig
from wintersession.tables import LtdCourseTable, CourseTable, AttendanceTable#, StudentTable,
from wintersession.time_decode import decode, decode_time
from django.core.urlresolvers import reverse
from wintersession.forms import AttendanceForm, AgendaPrivacyForm, FriendAgendaForm
from django.forms.models import modelformset_factory, modelform_factory
from django_cas.decorators import login_required
from django.contrib.auth.decorators import user_passes_test as django_user_passes_test
from utils.dsml import gdi
import datetime
from pytz import timezone
import collections
from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.auth.views import login
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.conf import settings
from models import Section

# Wintersession registration start
TIMEZONE = timezone('US/Eastern')
REGSTART = TIMEZONE.localize(datetime.datetime(year=2017,
                                               month=1,
                                               day=13,
                                               hour=0,
                                               minute=0,
                                               second=1))
REGEND   = TIMEZONE.localize(datetime.datetime(year=2017,
                                               month=1,
                                               day=29,
                                               hour=23,
                                               minute=59,
                                               second=59))

def home(request):
    return render(request, 'wintersession/home.html', {})

def teach(request):
    return render(request, 'wintersession/teach.html', {})

def about(request):
    return render(request, 'wintersession/about.html', {})

def enroll(request):
    courses = Course.objects.filter(cancelled=False)
    table = LtdCourseTable(courses)
    RequestConfig(request).configure(table)
    return render(request, 'wintersession/enroll.html', {'table': table})

@login_required
def student(request, error_message=None):
    user_name = request.user
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('login')) # Send to CAS
    if Student.objects.filter(netID=user_name).count() != 1:
        info = gdi(user_name) # get personal info from LDAP
        s = Student(netID=user_name, first_name=info.get('givenName'),
                    last_name=info.get('sn')) # need to include other fields, too!
        s.save()
        # Add the special event
        c = Course.objects.get(courseID='S1499')
        Registration(course=c, student=s).save()
    student = Student.objects.get(netID=user_name)
    identity = (student.netID, student.first_name, student.last_name)
    my_registrations = student.registration_set.all()
    my_courses = student.course_set.all()
    table = CourseTable(my_courses)
    RequestConfig(request).configure(table)
    # Only active courses
    active_courses = Course.objects.filter(cancelled=False)
    c_ids = [o.courseID for o in active_courses if not o.is_full()] # can remove
    # Only non-full active courses
    avail_courses = active_courses.filter(courseID__in=c_ids)       # can remove
    context = {
        'identity' : identity,
        'my_registrations' : my_registrations,
        'active_courses' : avail_courses, # or active_courses
        'error_message' : error_message,
        'table' : table,
    }
    return render(request, 'wintersession/student.html', context)

def courses(request):
    courses = Course.objects.filter(cancelled=False).exclude(courseID__regex=r'^.*\.[^a].*$')
    course_count = courses.count()
    #     cl = []
    #     prev_c = Course(title=None)
    #     for c in courses:
    #         if c.title != prev_c.title:
    #             cl.append(c)
    #         prev_c = c
    context = {
        'courses' : courses,
        'num_c' : course_count,
        }
    return render(request, 'wintersession/courses.html', context)

@csrf_protect
@login_required
def register(request):
    user_name = request.user
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('login')) # Send to CAS
    if Student.objects.filter(netID=user_name).count() != 1:
        info = gdi(user_name) # get personal info from LDAP
        s = Student(netID=user_name, first_name=info.get('givenName'),
                    last_name=info.get('sn')) # need to include other fields, too!
        s.save()
        # Add the special event
        c = Course.objects.get(courseID='S1499')
        Registration(course=c, student=s).save()
    context = {
        'REGSTART': REGSTART,
        'REGEND': REGEND
    }
    return render(request, 'wintersession/register.html', context)

@login_required
def instructor(request):
    user_name = request.user
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('login')) # Really needs to send to CAS
    if Instructor.objects.filter(netID=user_name).count() != 1:
        err_msg = "You're not an instructor."
#         return HttpResponseRedirect(reverse('wintersession:student', args=(err_msg,)))
        return student(request, err_msg)
#         return redirect('wintersession:student', error_message=err_msg)
    selected_instructor = Instructor.objects.get(netID=user_name)
    identity = (selected_instructor.netID, selected_instructor.first_name, selected_instructor.last_name)
    my_courses = selected_instructor.course_set.all()
    course_table = CourseTable(my_courses)
    RequestConfig(request).configure(course_table)
    registration_tables = {}
#     for course in my_courses:
#         student_table = StudentTable(course.students.all())
#         RequestConfig(request).configure(student_table)
#         student_tables[course.title] = student_table

    for mc in my_courses:
        registrations = Registration.objects.filter(course=mc).order_by('student__last_name')
        students = Student.objects.filter(registration__course=mc).order_by('last_name')
        registration_table = AttendanceTable(registrations)
        RequestConfig(request).configure(registration_table)
        registration_tables[mc.title] = registration_table

    context = {
        'identity' : identity,
#         'my_courses' : my_courses,
        'course_table' : course_table,
        'registration_tables' : registration_tables,
    }

    return render(request, 'wintersession/instructor.html', context)

# def attendance(request):
#     formset = modelformset_factory(Registration, form=AttendanceForm, extra=0)(request.POST)
#     formset.save()

@login_required
def drop(request):
    try:
        selected_course = Course.objects.get(courseID=request.POST['course'])
    except (KeyError, Course.DoesNotExist):
        error_message = "That course does not exist."
        return student(request, error_message)
    else:
        now = TIMEZONE.localize(datetime.datetime.now())
        if not (REGSTART <= now <= REGEND):
            error_message = "It is not time to enroll."
            return student(request, error_message)
        selected_student = Student.objects.get(netID=request.user)
        #for item in selected_course.blocks:
        #    selected_student.blocks.remove(item)
        #selected_student.save()
        Registration.objects.filter(student=selected_student,course=selected_course).delete()
        error_message = selected_course.title+" successfully dropped."
        return student(request, error_message)

@login_required
def add(request):
    try:
        selected_course = Course.objects.get(courseID=request.POST['course'])
    except (KeyError, Course.DoesNotExist):
        error_message = "That course does not exist."
        return student(request, error_message)
    else:
        now = TIMEZONE.localize(datetime.datetime.now())
        if not (REGSTART <= now <= REGEND):
            error_message = "It is not time to enroll."
            return student(request, error_message)
        selected_student = Student.objects.get(netID=request.user)
        ss_courses = selected_student.course_set.all()
        # Can't enroll in a class we're already in
        if selected_course in ss_courses:
            error_message = "Already enrolled in "+selected_course.title
            return student(request, error_message)
        # Can't enroll in a full class
        if selected_course.is_full():
            error_message = selected_course.title+" is at maximum capacity."
            return student(request, error_message)
        # Can't enroll in a cancelled class
        if selected_course.cancelled:
            error_message = selected_course.title+" is cancelled."
            return student(request, error_message)
        # Can't enroll in two section of same class
        if selected_course.other_section.count() != 0:
            other_sections = selected_course.other_section.all()
            my_courses = selected_student.course_set.all()
            for course in my_courses:
                for section in other_sections:
                    if course.courseID == section.courseID:
                        error_message = "You are already in "+section.courseID+", which is an alternative section of "+course.title
                        return student(request, error_message)
        # Can't enroll in a class with time conflicts
        ssb = selected_student.blocks()
        overlap = False
        for blk in selected_course.blocks:
            if blk in ssb:
                overlap = True
                break
        if overlap:
            for course in selected_student.course_set.all():
                for blk in course.blocks:
                    if blk in selected_course.blocks:
                        error_message = selected_course.title \
                        +" conflicts with "+course.title+" at " \
                        +decode(blk)
                        return student(request, error_message)
        # If we've made it to here, we can enroll
        #for item in selected_course.blocks:
        #    selected_student.blocks.append(item)
        #selected_student.save()
        Registration(student=selected_student, course=selected_course).save()
        error_message = selected_course.title+" successfully added."
        return student(request, error_message)

@login_required
def my_agenda(request):
    return redirect('agenda', student_id=request.user)

@login_required
def agenda(request, student_id):
    selected_student = get_object_or_404(Student, netID=student_id)
    selected_identity = (selected_student.netID, selected_student.first_name, selected_student.last_name)
    user_student = Student.objects.get(netID=request.user)
    user_identity = (user_student.netID, user_student.first_name, user_student.last_name, user_student.pk)
    # Is the user looking at his own agenda?
    own_agenda = (selected_student == user_student)
    ss_courses = selected_student.course_set.all()
#    ss_blocks = selected_student.blocks().sort()
    agend = {}
    for i in range(0, 7):
        agend[i] = {}
    # We're going to make a dict with five entries. Values will be dicts for
    # each day of the week. the subdicts will map start timecodes to tuples
    # with format (Course, start time, end time)
    # for each course the student is taking
    for c in ss_courses:
        prev_blk = 0
        first_blk = c.blocks[0]
        # and for each block in that course
        for blk in c.blocks:
            # see if the block is beginning of the session
            # if not, go to the next block
            if blk == prev_blk + 5:
                prev_blk = blk
                continue
            # but if so, record the previous session
            dow = first_blk / 1000
            start_time = decode_time(first_blk % 1000)
            end_time = decode_time((prev_blk+5) % 1000)
            info = (c, start_time, end_time)
            agend[dow][first_blk] = info
            # and start a new one
            first_blk = blk
            prev_blk = blk
        else: # Handle the last session
            dow = int(str(first_blk)[0])
            start_time = decode_time(first_blk % 1000)
            end_time = decode_time((prev_blk+5) % 1000)
            info = (c, start_time, end_time)
            agend[dow][first_blk] = info

    # now order all of the dictionaries
    for i in range(1,6):
        od = collections.OrderedDict(sorted(agend[i].items()))
        agend[i] = od

    dow = {}
    dow[0] = "Sunday"
    dow[1] = "Monday"
    dow[2] = "Tuesday"
    dow[3] = "Wednesday"
    dow[4] = "Thursday"
    dow[5] = "Friday"
    dow[6] = "Saturday"

    # Prepare the privacy option form if user is looking at own agenda
    if own_agenda:
        privacy_form = AgendaPrivacyForm(instance=user_student)
        agenda_visibility = True
    else:
        privacy_form = None
        agenda_visibility = selected_student.agenda_visibility

    # Preare the search for friend form
    friend_form = FriendAgendaForm()

    context = {
               'agenda' : agend,
               'dow' : dow,
               'own_agenda' : own_agenda,
               'user_identity' : user_identity,
               'selected_identity' : selected_identity,
               'privacy_form' : privacy_form,
               'agenda_visibility' : agenda_visibility,
               'friend_form' : friend_form,
               }

    if request.method == 'POST' and own_agenda:
        privacy_form = AgendaPrivacyForm(request.POST)
        if privacy_form.is_valid():
            a_v = privacy_form.cleaned_data['agenda_visibility']
            user_student.agenda_visibility = a_v
            user_student.save()
            # ugly hack to get forms to refresh
            request.method = 'GET'
            return agenda(request, user_student.netID)
        else:
            raise RuntimeError("Form was not valid")

    return render(request, 'wintersession/agenda.html', context)

@login_required
def friend_agenda(request):
    if request.method == 'POST':
        form = FriendAgendaForm(request.POST)
        if form.is_valid():
            return redirect('agenda',student_id=form.cleaned_data['friend_netID'])
        else:
            return redirect('agenda',student_id=request.user)
    else:
        return redirect('agenda',student_id=request.user)

def events(request):
    return render(request, 'wintersession/events.html', {})

def admin(request):
    if not request.user.is_staff:
        defaults = {
            'template_name': 'admin/login.html',
            'authentication_form': AdminAuthenticationForm,
            'extra_context': {
                'title': 'Log in',
                'app_path': request.get_full_path(),
                REDIRECT_FIELD_NAME: request.get_full_path(),
                },
            }
        return login(request, **defaults)

    context = {
        'courses': Course.objects.all(),
        'user': request.user
    }
    return render(request, 'wintersession/admin.html', context)

@django_user_passes_test(lambda u: u.is_staff)
@require_POST
def admin_email(request):
    to_emails = [netID + '@princeton.edu' for netID in Student.objects.all().values_list('netID', flat=True)]
    email = EmailMessage(subject=request.POST['subject'],
                         body=request.POST['message'],
                         from_email=settings.DEFAULT_FROM_EMAIL,
                         to=[settings.DEFAULT_FROM_EMAIL],
                         bcc=to_emails)
    email.send()
    return redirect('admin')


def course_conflicts(course, new_blocks):
    conflicting_students = []
    non_conflicting_students = []
    for student in course.students.all():
        ssb = student.blocks()
        overlap = False
        for blk in new_blocks:
            if blk in ssb:
                overlap = True
                break
        if overlap:
            conflicting_courses = []
            for course in student.course_set.all():
                for blk in course.blocks:
                    if blk in new_blocks:
                        conflicting_courses.append(course)
                        break
            conflicting_students.append((student, conflicting_courses))
        else:
            non_conflicting_students.append(student)
    return conflicting_students, non_conflicting_students

@require_GET
def admin_reschedule_check(request):
    courseID = request.GET['courseID']
    course = Course.objects.get(courseID=courseID)
    new_blocks_text = request.GET['new_blocks']
    new_blocks = [int(x) for x in new_blocks_text.replace("[", "").replace("]", "").replace(" ", "").split(",")]

    conflicting_students, non_conflicting_students = course_conflicts(course, new_blocks)

    context = {
        'courseID': courseID,
        'new_blocks_text': new_blocks_text,
        'course': course,
        'new_section': Section(new_blocks),
        'conflicting_students': conflicting_students,
        'conflicting_students_flat': ", ".join([student.netID + "@princeton.edu" for student, courses in conflicting_students]),
        'non_conflicting_students': non_conflicting_students,
        'non_conflicting_students_flat': ", ".join([student.netID + "@princeton.edu" for student in non_conflicting_students])
    }
    return render(request, 'wintersession/admin_reschedule_check.html', context)

@require_POST
def admin_reschedule(request):
    courseID = request.POST['courseID']
    course = Course.objects.get(courseID=courseID)
    new_blocks_text = request.POST['new_blocks_text']
    new_blocks = [int(x) for x in new_blocks_text.replace("[", "").replace("]", "").replace(" ", "").split(",")]

    conflicting_students, non_conflicting_students = course_conflicts(course, new_blocks)

    for student, other_course in conflicting_students:
        Registration.objects.filter(student=student, course=course).delete()

    course.blocks = new_blocks_text
    course.save()

    return redirect('admin')
