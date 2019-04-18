import django, os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SubGit.settings")
django.setup()
from upload.models import Course, Assignment

intro, new = Course.objects.get_or_create(id="cs111.00-f18", number="CS 111", section="00",
                             title="Introduction to Computer Science",
                             prof="Eric Alexander")

Course.objects.get_or_create(id="cs211.00-f18", number="CS 211", section="00",
                             title="Data Structures", prof="Anna Rafferty")

Course.objects.get_or_create(id="cs211.01-f18", number="CS 211", section="01",
                             title="Data Structures", prof="Layla Oesper")

Course.objects.get_or_create(id="cs348.00-f18", number="CS 348", section="00",
                             title="Parallel and Distributed Computing",
                             prof="Dave Musicant")

Assignment.objects.get_or_create(title="Language Modeling with N-Grams", course=intro)
Assignment.objects.get_or_create(title="Solve a Maze", course=intro)