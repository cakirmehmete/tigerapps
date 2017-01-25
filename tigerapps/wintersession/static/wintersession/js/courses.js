window.App = Ember.Application.create({
    rootElement: '#wsite-content'
});

App.ApplicationAdapter = DS.FixtureAdapter;

DS.RESTAdapter.reopen({
    headers: {
        "X-CSRFToken": window.CSRF_TOKEN
    }
});

App.Router.map(function() {
    this.resource('courses', { path: '/' });
});

App.ApplicationRoute = Ember.Route.extend({
    model: function() {
        this.store.find('course');
        this.store.find('section');
        this.store.find('block');
    }
});

App.CoursesRoute = Ember.Route.extend({
    model: function() {
        return Ember.RSVP.hash({
            courses: this.store.find('course'),
            registrations: this.store.find('registration')
        });
    }
});

App.CoursesController = Ember.ObjectController.extend({
    actions: {
        registerSection: function(section) {
            var newReg = this.store.createRecord('registration', {
                section: section
            });
            newReg.save().catch(function(err) {
                alert(err['responseJSON']['registration']['error']);
                newReg.rollback();
                newReg.unloadRecord();
            });
        },
        unregisterSection: function(section) {
            var reg = section.get('registration');
            reg.destroyRecord().catch(function(err) {
                alert(err['responseJSON']['registration']['error']);
                reg.rollback();
            });
        },
        doFilter: function() {
            this.set('filter', this.get('filterValue'));
        },
        clearFilter: function() {
            this.set('filterValue', '');
            this.set('filter', '');
        },
        refresh: function() {
            this.set('isRefreshing', true);
            var self = this;
            Ember.RSVP.hash({
                courses: this.store.find('course'),
                registrations: this.store.find('registration')
            }).then(function() {
                self.set('isRefreshing', false);
            });
        }
    },
    isRefreshing: false,
    isSearching: false,
    filter: '',
    filterValue: '',
    filterUpdate: function() {
        this.set('isSearching', true);
        Ember.run.debounce(this, this.doFilter, 500);
    }.observes('filterValue'),
    doFilter: function() {
        this.set('filter', this.get('filterValue'));
    },
    filteredContent: function() {
        this.set('isSearching', false);
        $("#course_catalog").scrollTop(0);

        var filter = this.get('filter');
        var courses = this.get('courses').filterBy('cancelled', false);
        if (filter == '') {
            return courses;
        } else {
            var search = new BitapSearcher(filter);
            return courses.filter(function(course) {
                var result = search.search(course.get('title'));
                course.set('score', result.score);
                return result.isMatch;
            }).sort(function(a, b) {
                return a.get('score') - b.get('score');
            });
        }
    }.property('filter', 'courses.@each.title'),
    filteredRegistrations: function() {
        return this.get('registrations').filterBy('isDirty', false).sortBy('courseTitle');
    }.property('registrations.@each.courseTitle', 'registrations.@each.isDirty'),
    sortedRegistrationsProperties: ['courseTitle:asc'],
    sortedRegistrations: Ember.computed.sort('registrations', 'sortedRegistrationsProperties'),
    isTimeToEnroll: function() {
        return (window.REGSTART <= new Date() && new Date() <= window.REGEND);
    }.property()
});

App.ApplicationAdapter = DS.RESTAdapter.extend({
    namespace: 'api'
});

App.Course = DS.Model.extend({
    title: DS.attr('string'),
    description: DS.attr('string'),
    cancelled: DS.attr('boolean'),
    room: DS.attr('string'),
    instructors: DS.attr(),
    sections: DS.hasMany('sections', {async: true}),
    isRegistered: function() {
        var isRegistered = false;
        this.get('sections').forEach(function(section) {
            if (section.get('registration') != null) {
                isRegistered = true;
            }
        });
        return isRegistered;
    }.property('sections.@each.registration'),
    instructors_string: function() {
        return this.get('instructors').join(', ')
    }.property('instructors')
});

App.Section = DS.Model.extend({
    course: DS.belongsTo('course', {async: true}),
    blocks: DS.hasMany('blocks', {async: true}),
    schedule: DS.attr(),
    schedule_string: DS.attr('string'),
    room: DS.attr('string'),
    current_enroll_other_students: DS.attr('number'),
    current_enroll: function() {
        return this.get('current_enroll_other_students') + (this.get('isRegistered') ? 1 : 0);
    }.property('isRegistered'),
    max_enroll: DS.attr('number'),
    is_full: DS.attr('boolean'),
    registration: DS.belongsTo('registration'),
    isRegistered: function() {
        return this.get('registration') != null;
    }.property('registration'),
    isConflicting: function() {
        return this.get('conflictText') != null;
    }.property('conflictText'),
    conflictText: function() {
        // Hack to handle OA courses
        if (this.get('course').get('title').substring(0,3) == 'OA ') {
            return '&nbsp;<b><a href="https://oa.princeton.edu/TripStore" target="_blank"><i class="fa fa-external-link"></i> Register on OA site</a></b>';
        }

        // Not conflicting if already registered
        if (this.get('isRegistered')) {
            return null;
        }

        // Conflicting if already registered in another section
        if (this.get('course').get('isRegistered')) {
            return 'Already registered for course';
        }

        // Check if full
        if (this.get('is_full')) {
            return 'Section is full';
        }

        // Check time conflicts
        var conflictText = null;
        this.get('blocks').forEach(function(block) {
            if (block.get('isRegistered')) {
                conflictText = 'Conflicts with course ' + block.get('registeredSection').get('course').get('title');
            }
        });

        return conflictText;
    }.property('blocks.@each.isRegistered', 'course.isRegistered')
});

App.Registration = DS.Model.extend({
    section: DS.belongsTo('section', {async: true}),
    courseTitle: function() {
        try {
            return this.get('section').get('course').get('title');
        } catch (e) {
            return '';
        }
    }.property('section.course.title')
});

App.BlockAdapter = DS.FixtureAdapter.extend({
    simulateRemoteResponse: false,
    latency: 0
});

App.Block = DS.Model.extend({
    sections: DS.hasMany('sections', {async: true}),
    isRegistered: function() {
        return this.get('registeredSection') != null;
    }.property('registeredSection'),
    registeredSection: function() {
        var registeredSection = null;
        this.get('sections').forEach(function(section) {
            if (section.get('isRegistered')) {
                registeredSection = section;
            }
        });
        return registeredSection;
    }.property('sections.@each.isRegistered')
});

App.Block.reopenClass({
    FIXTURES: []
});

window.AppConstants = {
    START_TIME: 8, // 8a
    END_TIME:   22  // 10p
};

Ember.Handlebars.helper('courseScheduleItem', function(courseTitle, startTime, endTime) {
    var top = (startTime - AppConstants.START_TIME) / (AppConstants.END_TIME - AppConstants.START_TIME + 1) * 100;
    var height = (endTime - startTime) / (AppConstants.END_TIME - AppConstants.START_TIME + 1) * 100;
    return new Ember.Handlebars.SafeString('<div class="course_schedule_item" style="top: ' + top + '%; height: ' + height + '%">' + courseTitle + '</div>');
});
