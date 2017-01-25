from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
admin.autodiscover()

# Authentication urls
urlpatterns = patterns('django_cas.views',
    (r'^login/?$', 'login'),
    (r'^logout/?$', 'logout'),
)

# Normal urls
urlpatterns += patterns('rooms.views',
    (r'^$', 'index'),
    (r'^map', 'map'),
    (r'^table', 'table'),
    (r'^test', 'index'),
#    (r'^drawid/(?P<drawid>\d{1})$', 'draw'),
#    (r'^create_queue/(?P<drawid>\d{1})$', 'create_queue'),
#    (r'^invite_queue/?$', 'invite_queue'),
#    (r'^respond_queue/?$', 'respond_queue'),
#    (r'^leave_queue/?$', 'leave_queue'),
#    (r'^get_room/(?P<roomid>\d+)', 'get_room'),
#    (r'^get_room/', 'bad_room'),
#    # Admin interface
#    (r'^admin/', include(admin.site.urls)),
#    (r'^user_settings.html$','settings'),
#    (r'^confirm_phone.html$','confirm_phone'),
#    (r'^manage_queues.html$','manage_queues'),
#    (r'^about/?$','about'),
)

# Real-time urls
# real_time_patterns = patterns('rooms.real_time_views',
#                               (r'^update_queue/(?P<drawid>\d{1})$',
#                                'update_queue'),
#                               (r'^get_queue/(?P<drawid>\d{1})$', 'get_queue'),
#                               (r'^get_queue/(?P<drawid>\d{1})/(?P<last_version>\d+)$',
#                                'get_queue'),
#                               (r'^start_simulation/(?P<delay>\d+)/(?P<size>\d+)$',
#                                'start_simulation'),
#                               (r'^start_simulation/(?P<delay>\d+)$',
#                                'start_simulation'),
#                               (r'^stop_simulation/?$', 'stop_simulation'),
#                               (r'^check_availability/(?P<timestamp>\d+)$',
#                                'check_availability'),
# )

# if settings.IS_REAL_TIME_SERVER:
#     urlpatterns += real_time_patterns
