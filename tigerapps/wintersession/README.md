This app powers the course registration system for Wintersession, a week of student-run classes during Intersession each year.

URL: http://wintersession.tigerapps.org/

# Use

First, I suggest logging in as a student by hitting Enroll -- you'll be prompted to log in with your netid.

Then, in an incognito window, you can open the admin panel (http://wintersession.tigerapps.org/admin/) and log in with staff credentials. Once you're logged in, hit the "Django Admin" button. You'll see all data tables there.

To add new courses, hit Courses, then "Add course" on the top right. Here's how to fill out the form:

* Course ID: enter some kind of numerical ID, like 10000. But if the course has a hard enrollment cap, put an E in front of the course ID, e.g. E10000. Make sure these are unique.
* Description, Cancelled, Room: self-explanatory
* Title: if you add "(External)", without the quotes, at the beginning of the course title, users will be prompted to look at the course description for external enrollment information. If the course title starts with "OA", the student will be prompted to visit the OA website.
* Min enroll: leave this at 0.
* Max enroll: the system will allow enrollment up to this number if the course has a hard cap, or up to 30% more than this number otherwise.
* Blocks: this field encodes times when the course occurs. Each meeting should be written as: `[days of week] [start]-[end]`. Separate meetings with an `&`.
Days of the week should be written as: `Su`, `M`,`Tu`,`W`,`Th`,`F`,`Sa`. Valid examples:
    * `M W Th 10:00am-11:00am & Tu F 6pm-7:30pm`
    * `Tu Th 10am-11:30am`
    * `M 10:00AM-11:00AM & Tu 06:00PM-07:30PM`
* Schedule: this field isn't used; set it to TBD.
* Instructors: these users will have special access to the course and their names will be shown to students. Either choose from among available instructors, or hit the green + button to the right of "Chosen Instructors" to add a new instructor. (When adding an instructor, you'll be asked whether the instructor is a faculty member. I think this just means that their hours are not tracked.)
* Other sections of the same course: Separate parallel sections are stored as separate courses. This is where you can connect two parallel sections -- you can choose another course you've already added, or hit the + button to create it in-line.

## Possible gotchas

* netID-email alias discrepancies: there is sometimes a difference between someone's netid and their email address. This means that some instructor email addresses might not match their netids. When they log in with their netids, the system might not realize they're the same instructor as the email addresses on file (added through the Add Instructor form you can trigger when adding a course). If an instructor is unable to access their list of students, this means their instructor entry in the Instructors table should be changed to reflect their actual netid.



# Development

## Architecture

Django powers the backend and is in charge of rendering most pages. The registration page is an Ember app which communicates with the Django backend via a REST API. Registration constraints, such as whether the student is trying to register for a class that conflicts with another they already chose, are checked on both the frontend and backend.


## Admin

There are two separate admin systems. Navigating to /admin brings you to the custom admin page, which has a couple of admin tools. Navigating to /djadmin (linked from the /admin page) brings you to the Django admin panel, which is where you can add/update courses under the “Wintersession” section.


## Models

An Instructor represents one teacher for a class. They are identified by their netIDs. 

Each of these Instructors may be linked to one or more Courses, which represent a particular section of a course being taught. Each course may be associated with more than one instructor. If there are multiple sections of one course, there must be multiple Course models created, as each Course represents one scheduled section. Each section needs to have its own ID. However, in this case, only the title/description/instructor/etc. of the first Course (ordered by ID) will be displayed on the site. Link the sections together by specifying the “other sections of the same course” field.

The schedule of a Course is represented by a “block” system, where each block corresponds to a half-hour slice of time within the week. A block needs to be explicitly entered for every slice of time that the Course takes up. For example, if a course takes place between 3-6pm on Tuesday and Thursday, a total of 12 blocks need to be specified. The blocks are stored as a list of 4-digit numbers in the following format:

* First digit: Day of the week, with 0=Sunday and 7=Saturday.
* Next 2 digits: Starting hour in 24-hour time. Be sure to pad the starting 0 if the time is 9am or earlier.
* Last digit: “0” if the block starts at :00, and “5” if the block starts at :30.

(This format means that the last three digits of the block number correspond to the number of 6-minute increments since midnight, except you can only specify them in half-hour intervals. Aside: this blocks system is used in the frontend for schedule conflict detection.)

Example: A section scheduled for 10a-11:30a on Tuesday and Thursday should have the following in the “blocks” field: `[2100, 2105, 2110, 4100, 4105, 4110]`

The “Schedule” field is not used, but currently is still marked as required by the schema. You can just fill in “TBD” or anything else in this field. The system will automatically format the correct schedule on the website based on the blocks field.

Specify the class capacity in the “Max enroll” field. Leave the “Min enroll” field at 0. Note that the system will allow 30% over-enrollment over this max value (and display this inflated cap on the website) unless you specify that it should be an exact cap (see below).

Check the “Cancelled” box to mark the section as cancelled on the website.

The course ID should be manually specified. There are special ID formats to enforce certain conditions. A course ID starting with “E” will strictly enforce the registration cap you specify and won’t allow over-enrollment.

The course name/title can also be used to redirect to external enrollment links. A course title starting with “OA” will not allow enrollment through the system directly, and instead display a link to the Outdoor Action website. A course title starting with "(External)" will show a message pointing to the user to examine the course description for external enrollment information.

When a student logs into the website to register for courses, a Student is automatically created in the database with their netID. When they register for some section of a course, a Registration is created that links the Student to the Course.


### Sample data

In JSON fixtures format:

```
[
    {
        "fields": {
            "faculty": false,
            "first_name": "Aded",
            "last_name": "Yako",
            "netID": "aayako"
        },
        "model": "wintersession.instructor",
        "pk": 1
    },
    {
        "fields": {
            "faculty": true,
            "first_name": "Christopher",
            "last_name": "Campisano",
            "netID": "ccampisa"
        },
        "model": "wintersession.instructor",
        "pk": 2
    },
    {
        "fields": {
            "blocks": "[5110, 5115, 5120, 5125]",
            "cancelled": false,
            "courseID": "10059",
            "description": "\"Ever wonder how YouTube beauty gurus and Instagram models have their hair and makeup on point, 24/7? Want to look your best for class, formals, and dates with bae? Have a hard time finding a local salon that specializes in curly and kinky hair? Look no further. Come take a crash course on hair and makeup!\r\n\r\n- Use what you've learned in this crash course and purchase the best products for your hair, skin type, and skin tone.\r\n- We're visiting the local mall to buy makeup, transportation will be provided!\r\n",
            "instructors": [
                81,
                124
            ],
            "max_enroll": 50,
            "min_enroll": 0,
            "other_section": [],
            "room": "McCosh 28",
            "schedule": "TBD",
            "title": "Beauty in Color: Shopping"
        },
        "model": "wintersession.course",
        "pk": 1
    }
]

```

# TODOs

* [ ] Change hacky "(External)" course title handling (see `courses.js`) to a proper flag for marking courses that have external registration links.