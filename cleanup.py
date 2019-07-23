import shutil
import os
from SubGit.settings import MEDIA_ROOT
from github import Github
from decouple import config
import sys

if len(sys.argv) != 2:
    print("Usage:\n\t$ python3 cleanup.py <username>\n")
    quit()

username = sys.argv[1]
repo_name = "csXXX-{}".format(username)

try:
    shutil.rmtree(MEDIA_ROOT)
except FileNotFoundError:
    print("File not found: {}".format(MEDIA_ROOT))

g = Github(config("GITHUB_ADMIN_USERNAME"), config("GITHUB_ADMIN_PASSWORD"))

# try:
#     repo = g.get_user().get_repo(repo_name)
#     repo.delete()
# except UnknownObjectException:
#     print("Repo not found: {}".format(repo_name))

for repo in g.get_user().get_repos():
    repo.delete()
