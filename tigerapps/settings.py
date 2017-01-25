# Django settings for tigerapps project.
import os, sys, socket
# Email/Database settings (sensitive info)
try:
    import local_settings
except ImportError, exp:
    sys.stderr.write("Warning: Couldn't import local_settings; missing passwords and other local data.  Using local_settings_blank instead.")
    import local_settings_blank as local_settings



CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CURRENT_DIR[:CURRENT_DIR.rfind('/')] + '/django_lib')


CURRENT_HOST = socket.gethostname()
if socket.gethostname() == "USGDev":
    CURRENT_HOST_PREFIX = "dev."
    CURRENT_HOME = "http://dev.tigerapps.org"
else:
    CURRENT_HOST_PREFIX = ""
    CURRENT_HOME = "http://www.tigerapps.org"


if 'IS_REAL_TIME_SERVER' in os.environ:
    IS_REAL_TIME_SERVER = True
else:
    IS_REAL_TIME_SERVER = False


REAL_TIME_PORT = os.environ.get('REAL_TIME_PORT', '8031')

#For django_cas
LOGIN_URL = '/login/'
#For paypal
PAYPAL_RECEIVER_EMAIL = 'agencies@princeton.edu'
#PAYPAL_RECEIVER_EMAIL = 'it@princetonusg.com'
#For sanitizer
SANITIZER_ALLOWED_TAGS = ('b', 'i', 'u', 'p', 'a', 'span', 'br', 'ul', 'li', 'ol')
SANITIZER_ALLOWED_ATTRIBUTES = ('href',)


#TODO: make DEBUG False on prod site when confident
DEBUG = True
TEMPLATE_DEBUG = DEBUG

#email gets sent to ADMINS if DEBUG == False
ADMINS = (('USG IT', 'it@princetonusg.com'),)
MANAGERS = ADMINS



DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'tigerapps',             # Or path to database file if using sqlite3.
        'USER': 'tigerapps',             # Not used with sqlite3.
        'PASSWORD': local_settings.DATABASE_PASSWORD,
        'HOST': '',             # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',             # Set to empty string for default. Not used with sqlite3.
    }
}
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}



SITE_ID = 1
# Make this unique, and don't share it with anybody.
SECRET_KEY = local_settings.SECRET_KEY



# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False



#MEDIA refers to user-generated files stored on the hard disk.
#TODO: Currently everything is stored in MEDIA
# Absolute path to the directory that holds media.
MEDIA_ROOT = CURRENT_DIR + '/media/'
# URL for media served from MEDIA_ROOT (need trailing slash).
MEDIA_URL = '/media/'
# permissions for uploaded files
FILE_UPLOAD_PERMISSIONS = 0664


#STATIC refers to CSS/js/img files.
#TODO: Currently everything is stored in MEDIA
# Absolute path to the directory that holds static files (must be diff from MEDIA_ROOT)
# Note: STATIC_ROOT is used when `manage.py collectstatic` is used,
#   STATICFILES_DIRS is used otherwise
STATIC_ROOT = CURRENT_DIR + "/../tigerapps_static/"
STATICFILES_DIRS = (CURRENT_DIR + "/static/",)
# URL for static files served from STATIC_ROOT (need trailing slash)
# Note that since Django 1.4, admin media files are automatically stored at STATIC_URL/admin/
STATIC_URL = "/static/"
# URL prefix for admin static files (need trailing slash). TODO: deprecated in django1.4
ADMIN_MEDIA_PREFIX = '/static/admin/'

#Used for staticfiles app. Files in this tuple are collected into STATIC_ROOT
#   when `manage.py collecstatic` is issued.
#STATICFILES_DIRS = (,)



# Tuples of imported modules...
# XXX: Should be independent of the authentication backend; since several apps
#   use customized auth backends, we set the auth backend in middleware.py
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#    'django.template.loaders.filesystem.load_template_source',
#    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'middleware.SubdomainsMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    # 'django.middleware.csrf.CsrfResponseMiddleware',

)

if IS_REAL_TIME_SERVER:
    MIDDLEWARE_CLASSES += ('middleware.RealTimeMiddleware',)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)


#APPEND_SLASH = True #TODO, we probably want this when ready to canonicalize the urls
#We get an error if we don't define a ROOT_URLCONF, even though we override it in SubdomainsMiddleware...
ROOT_URLCONF = 'www.urls'

TEMPLATE_DIRS = (
    CURRENT_DIR + '/templates',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.humanize',
    'django.contrib.staticfiles',
    'paypal.standard.ipn',
    'utils',
    'adminsortable',
    'south',
    'sanitizer',

# These apps are launched or in the process of being launched
# This means that they ARE sync'd with South
    'www',
    'cal',
    'dvd',
    'ptx',
    'ttrade',
    'card',
    'ccc',
    'elections',
    'pam',
    'pounce',
    'writetime',
    'rooms',
#    'newrooms',
    'pom',
    'sectionswap',
    'storage',
    'suggestions',
# These apps were never launched and there are no plans to launch them
# This means that they ARE NOT sync'd with South
#    'facebook',
#    'album',
    'my',
    'myapps',
    'groups',

# In development
    'wintersession',
    'django_tables2',
    'rest_framework',
    'django_verbatim',

)

# Context processor for django_tables2 (wintersession)
import django.conf.global_settings as DEFAULT_SETTINGS
TEMPLATE_CONTEXT_PROCESSORS = DEFAULT_SETTINGS.TEMPLATE_CONTEXT_PROCESSORS + (
    'django.core.context_processors.request',
)

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAdminUser'
    ]
}




