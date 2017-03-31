from rooms.models import *
from django.contrib import admin
#
#admin.site.register(Draw)
#admin.site.register(Building)
#admin.site.register(Room)
#admin.site.register(User)
#admin.site.register(Queue)
#admin.site.register(QueueInvite)
#admin.site.register(PastDraw)
#admin.site.register(PastDrawEntry)
#admin.site.register(Carrier)
#admin.site.register(Review)
#

class DisclaimerAdmin(admin.ModelAdmin):
    list_display = ('netid', 'date')
    list_filter = ['date']

admin.site.register(Disclaimer, DisclaimerAdmin)


class NewReviewAdmin(admin.ModelAdmin):
    list_display = ('summary', 'date', 'netid')
    list_filter = ['date']
    search_fields = ['content', 'summary', 'netid']

admin.site.register(NewReview,NewReviewAdmin)
