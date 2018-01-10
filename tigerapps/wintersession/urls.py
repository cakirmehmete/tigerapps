from django.conf.urls.defaults import patterns, url, include
from django.contrib import admin
from django.views.generic import RedirectView
from wintersession import views, api

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^enroll/$', RedirectView.as_view(url='/register/'), name='enroll'),
    url(r'^student/$', RedirectView.as_view(url='/register/'), name='student'),
    url(r'^courses/$', views.courses, name='courses'),
    url(r'^register/$', views.register, name='register'),
    url(r'^instructor/$', views.instructor, name='instructor'),
    url(r'^instructor/attendance$', views.instructor, name='attendance'),
    url(r'^student/drop/$', views.drop, name='drop'),
    url(r'^student/add/$', views.add, name='add'),
    url(r'^student/agenda/(?P<student_id>.{1,8})/$', views.agenda, name='agenda'),
    url(r'^student/agenda/$', views.my_agenda, name='agenda'),
    url(r'^student/friend_agenda/$', views.friend_agenda, name='friend_agenda'),
    url(r'^teach/$', views.teach, name='teach'),
    url(r'^about/$', views.about, name='about'),
    url(r'^events/$', views.events, name='events'),
    url(r'^$', views.home, name='home'),

    url(r'^admin/$', views.admin, name='admin'),
    url(r'^admin/email$', views.admin_email, name='admin_email'),
    url(r'^admin/reschedule_check', views.admin_reschedule_check, name='admin_reschedule_check'),
    url(r'^admin/reschedule', views.admin_reschedule, name='admin_reschedule'),
    url(r'^admin$', RedirectView.as_view(url='/admin/')),
    (r'^djadmin/', include(admin.site.urls)),

    # login/logout
    url(r'^login/?$', 'django_cas.views.login', name='login'),
    url(r'^logout/?$', 'django_cas.views.logout', name='logout'),

    url(r'^api/', include(api.router.urls, namespace='api')),
)
