import datetime
from pytz import timezone
from rest_framework import routers, serializers, viewsets, permissions, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_ember.parsers import EmberJSONParser
from rest_framework_ember.renderers import JSONRenderer
from rest_framework.response import Response
from wintersession import views
from wintersession.models import Student, Course, Registration
from wintersession.time_decode import decode
from wintersession.views import TIMEZONE


EMBER_PARSER_CLASSES = (EmberJSONParser, FormParser, MultiPartParser)
EMBER_RENDERER_CLASSES = (JSONRenderer,)


class InstructorNameField(serializers.RelatedField):
    def to_native(self, value):
        return value.full_name()


class CourseSerializer(serializers.ModelSerializer):
    instructors = InstructorNameField(many=True)
    sections = serializers.Field(source='all_section_ids')

    class Meta:
        model = Course
        fields = ('id', 'title', 'description', 'cancelled', 'room', 'instructors', 'sections')


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (permissions.AllowAny,)
    parser_classes = EMBER_PARSER_CLASSES
    renderer_classes = EMBER_RENDERER_CLASSES
    queryset = Course.objects.exclude(courseID__regex=r'^.*\.[^a].*$')
    serializer_class = CourseSerializer


class ScheduleField(serializers.Field):
    def to_native(self, value):
        output = []
        for day, times in value.iteritems():
            output.append(times)
        return output


class SectionSerializer(serializers.ModelSerializer):
    schedule = ScheduleField(source='this_section.as_dict')
    blocks = serializers.Field(source='blocks')
    schedule_string = serializers.Field(source='this_section.as_string')
    current_enroll_other_students = serializers.SerializerMethodField('current_enroll_other_students_method')
    max_enroll = serializers.Field(source='max_enroll_with_extra')
    is_full = serializers.Field(source='is_full')

    def current_enroll_other_students_method(self, obj):
        request = self.context.get('request', None)
        return obj.current_enroll_exclude(netID=request.user)

    class Meta:
        model = Course
        fields = ('id', 'blocks', 'schedule', 'schedule_string', 'room', 'current_enroll_other_students', 'max_enroll', 'is_full')


class SectionViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (permissions.AllowAny,)
    parser_classes = EMBER_PARSER_CLASSES
    renderer_classes = EMBER_RENDERER_CLASSES
    queryset = Course.objects.all()
    serializer_class = SectionSerializer
    resource_name = 'section'


class RegistrationSerializer(serializers.ModelSerializer):
    section = serializers.PrimaryKeyRelatedField(source='course')

    class Meta:
        model = Registration
        fields = ('id', 'section')



class RegistrationViewSet(viewsets.mixins.CreateModelMixin,
                          viewsets.mixins.RetrieveModelMixin,
                          viewsets.mixins.DestroyModelMixin,
                          viewsets.mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = EMBER_PARSER_CLASSES
    renderer_classes = EMBER_RENDERER_CLASSES
    serializer_class = RegistrationSerializer

    def get_queryset(self):
        student = Student.objects.get(netID=self.request.user)
        return student.registration_set.all()

    def pre_save(self, obj):
        obj.student = Student.objects.get(netID=self.request.user)

    def pre_delete(self, obj):
        obj.student = Student.objects.get(netID=self.request.user)

    def create(self, request, *args, **kwargs):
        error_message = None

        try:
            selected_course = Course.objects.get(id=request.DATA['section'])
        except (KeyError, Course.DoesNotExist):
            error_message = "That course does not exist."
        else:
            now = TIMEZONE.localize(datetime.datetime.now())
            if not (views.REGSTART <= now <= views.REGEND):
                error_message = "It is not time to enroll."
            selected_student = Student.objects.get(netID=request.user)
            ss_courses = selected_student.course_set.all()
            # Can't enroll in a class we're already in
            if selected_course in ss_courses:
                error_message = "Already enrolled in "+selected_course.title
            # Can't enroll in a full class
            if selected_course.is_full():
                error_message = selected_course.title+" is at maximum capacity."
            # Can't enroll in a cancelled class
            if selected_course.cancelled:
                error_message = selected_course.title+" is cancelled."
            # Can't enroll in two section of same class
            if selected_course.other_section.count() != 0:
                other_sections = selected_course.other_section.all()
                my_courses = selected_student.course_set.all()
                for course in my_courses:
                    for section in other_sections:
                        if course.courseID == section.courseID:
                            error_message = "You are already in "+section.courseID+", which is an alternative section of "+course.title
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

        if error_message is not None:
            return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)

        # If we've made it to here, we can enroll
        return super(RegistrationViewSet, self).create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        error_message = None

        now = TIMEZONE.localize(datetime.datetime.now())
        if not (views.REGSTART <= now <= views.REGEND):
            error_message = "It is not time to enroll."

        if error_message is not None:
            return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)

        return super(RegistrationViewSet, self).destroy(request, *args, **kwargs)


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter(trailing_slash=False)
router.register(r'courses', CourseViewSet)
router.register(r'sections', SectionViewSet)
router.register(r'registrations', RegistrationViewSet, base_name='registration')
