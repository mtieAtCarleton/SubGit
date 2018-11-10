# from https://stackoverflow.com/questions/38594717/how-do-i-push-new-files-to-github
from git import Repo
from SubGit.settings import MEDIA_ROOT
from decouple import config
import os


def submit(user, fileName):
    #repo_dir = '{}/{}/'.format(MEDIA_ROOT, user)
    repo_dir = os.path.join(MEDIA_ROOT, user)
    print(repo_dir)
    repo = Repo(repo_dir)
    # file_list = [
    #     '{}/{}/{}'.format(MEDIA_ROOT, user, fileName)
    # ]
    file_list = [
        os.path.join(MEDIA_ROOT, user, fileName)
    ]
    print(file_list)
    commit_message = 'Testing push of {}/{}'.format(user, fileName)
    repo.index.add(file_list)
    repo.index.commit(commit_message)
    origin = repo.remote('origin')
    origin.pull()
    origin.push()
