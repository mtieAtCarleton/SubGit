import django, os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SubGit.settings")
django.setup()
from upload.models import Course, Assignment
from django.utils.dateparse import parse_date
from datetime import datetime
from django.utils.timezone import make_aware
import pytz

intro, new = Course.objects.get_or_create(id="cs111.00-f18", number="CS 111", section="00",
                             title="Introduction to Computer Science",
                             prof="Eric Alexander")

ds1, _ = Course.objects.get_or_create(id="cs211.00-f18", number="CS 211", section="00",
                             title="Data Structures", prof="Anna Rafferty")

Course.objects.get_or_create(id="cs211.01-f18", number="CS 211", section="01",
                             title="Data Structures", prof="Layla Oesper")

Course.objects.get_or_create(id="cs348.00-f18", number="CS 348", section="00",
                             title="Parallel and Distributed Computing",
                             prof="Dave Musicant")
Course.objects.get_or_create(id="cs000-000", number="CS 000", section="00",
                             title="testy test",
                             prof="testy test")

Assignment.objects.get_or_create(title="Language Modeling with N-Grams", course=intro)
Assignment.objects.get_or_create(title="Solve a Maze", course=intro)
Assignment.objects.get_or_create(title="Let's Hash This Out", course=ds1, deadline=parse_date("2019-05-26"))
Assignment.objects.get_or_create(title="Trees are Losers", course=ds1,
                                 deadline=datetime(2019, 5, 27, 17, tzinfo=pytz.UTC))
Assignment.objects.get_or_create(title="Arrayed Against Us", course=ds1,
                                 deadline=datetime(2019, 5, 27, 22, tzinfo=pytz.UTC))
