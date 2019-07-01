import django, os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SubGit.settings")
django.setup()
from upload.models import Course, Assignment, Person, Submission
from django.utils.dateparse import parse_date
from datetime import datetime
from django.utils.timezone import make_aware
import pytz

test_prof = Person(username="dln", full_name="David Liben-Nowell")
test_prof.save()

test_prof2 = Person(username="ealexander", full_name="Eric Alexander")
test_prof2.save()

testgrader = Person(username="kemptond", full_name="Dylan Kempton")
testgrader.save()

intro, new = Course.objects.get_or_create(id="cs111.00-f18", number="CS 111", section="00",
                             title="Introduction to Computer Science",
                             prof=test_prof)

datastruct, new = Course.objects.get_or_create(id="cs201.00-f18", number="CS 201", section="00",
                             title="Data Structures",
                             prof=test_prof2)
datastruct.graders.add(testgrader)

Assignment.objects.get_or_create(title="Arrayed Against Us", course=intro,
                                 deadline=datetime(2019, 5, 27, 22, tzinfo=pytz.UTC))

assignment_one, new = Assignment.objects.get_or_create(title="Linked Lists", course=datastruct,
                                 deadline=datetime(2019, 7, 1, 22, tzinfo=pytz.UTC))

assignment_two, new = Assignment.objects.get_or_create(title="Zelda'd Lists", course=datastruct,
                                 deadline=datetime(2019, 7, 2, 22, tzinfo=pytz.UTC))

submission_one, new = Submission.objects.get_or_create(description="The Linkiest List",
                                submitted_at=datetime(2019, 6, 2, 22, tzinfo=pytz.UTC),
                                assignment=assignment_one)
