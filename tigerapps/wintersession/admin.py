from django.contrib import admin
from wintersession.models import Student,Instructor,Course,Registration
from django import forms
from blocks import *

class RegistrationInline(admin.TabularInline):
    model = Registration



class StudentAdmin(admin.ModelAdmin):
    inlines = [RegistrationInline]
    list_display = ('netID','first_name','last_name')
    fields = ('netID', 'first_name', 'last_name')
#    list_filter = ['last_name']
    search_fields = ['netID']



admin.site.register(Student, StudentAdmin)

class CourseInstructorInline(admin.TabularInline):
    model = Course.instructors.through #@UndefinedVariable
    extra = 2

class InstructorAdmin(admin.ModelAdmin):
    inlines = [CourseInstructorInline]
    list_display = ('netID','first_name','last_name','billable')
#    list_filter = ['last_name']
    search_fields = ['netID', 'first_name', 'last_name']

admin.site.register(Instructor, InstructorAdmin)

class OtherSectionInline(admin.TabularInline):
    model = Course.other_section.through #@UndefinedVariable
    fk_name = 'from_course'
    extra = 2
    verbose_name = "Other section of the same course"
    verbose_name_plural = "Other sections of the same course"

#A little hack to make blocks editing better. See also the BlocksField model
#to_python method
class BlocksWidget(forms.widgets.Input):
    input_type = 'text'

    def __init__(self, attrs=None):
        if attrs is not None:
            self.input_type = attrs.pop('type', self.input_type)
        super(BlocksWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        return super(BlocksWidget, self).render(name, blocks_to_friendly(value), attrs)


# Makes the blocks (a ListField which is subclass of TextField defaults Textarea)
# into a TextInput
class BlocksModelForm( forms.ModelForm ):
    blocks = forms.CharField( widget=BlocksWidget )
    class Meta:
        model = Course

class CourseAdmin(admin.ModelAdmin):
    list_display = ('courseID','title','schedule','room','current_enroll',
                    'max_enroll', 'meets_min_requirements','cancelled')
    search_fields = ['courseID','title']
    inlines = [OtherSectionInline]
    exclude = ('other_section',)
    filter_horizontal = ('instructors',)
    form = BlocksModelForm

admin.site.register(Course, CourseAdmin)

class RegistrationAdmin(admin.ModelAdmin):
#   fields = ['student', 'course', 'timestamp']
    list_display = ('course','student')
#    list_filter = ['course','student']
    search_fields = ['course__courseID','student__netID']

admin.site.register(Registration, RegistrationAdmin)
