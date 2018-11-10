import shutil
import os
from SubGit.settings import MEDIA_ROOT
from github import Github
from github.GithubException import UnknownObjectException
from decouple import config
import sys

if len(sys.argv) != 2:
    print("Usage:\n\t$ python3 cleanup.py <username>\n")
    quit()

username = sys.argv[1]
file_path = os.path.join(MEDIA_ROOT, username)
repo_name = "csXXX-{}".format(username)

try:
    shutil.rmtree(file_path)
except FileNotFoundError:
    print("File not found: {}".format(file_path))

g = Github(config("GITHUB_ADMIN_USERNAME"), config("GITHUB_ADMIN_PASSWORD"))

# try:
#     repo = g.get_user().get_repo(repo_name)
#     repo.delete()
# except UnknownObjectException:
#     print("Repo not found: {}".format(repo_name))

for repo in g.get_user().get_repos():
    repo.delete()
