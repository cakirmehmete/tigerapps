from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
import views

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
    url(r'^admin/', include(admin.site.urls)),
    (r'^disclaimer', 'disclaimer'),
    (r'^review/(?P<building>\d{4})/(?P<room>\w+)/view', 'view_reviews'),
    (r'^review/(?P<building>\d{4})/(?P<room>\w+)/add', 'add_review')
)
