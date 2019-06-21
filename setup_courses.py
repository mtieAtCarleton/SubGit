import django, os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SubGit.settings")
django.setup()
from upload.models import Course, Assignment, Person
from django.utils.dateparse import parse_date
from datetime import datetime
from django.utils.timezone import make_aware
import pytz

test_prof = Person(username="whiteg", full_name="Ginnie White")
test_prof.save()

intro, new = Course.objects.get_or_create(id="cs111.00-f18", number="CS 111", section="00",
                             title="Introduction to Computer Science",
                             prof=test_prof)

#Assignment.objects.get_or_create(title="Arrayed Against Us", course=ds1,
                                 #deadline=datetime(2019, 5, 27, 22, tzinfo=pytz.UTC))
