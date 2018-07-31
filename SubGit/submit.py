# from https://stackoverflow.com/questions/38594717/how-do-i-push-new-files-to-github
from git import Repo
from SubGit.settings import MEDIA_ROOT
from decouple import config

def submit(gitUsername, fileName):
    repo_dir = config('REPO_ROOT')
    print(repo_dir)
    repo = Repo(repo_dir)
    file_list = [
        '{}/uploads/{}/{}'.format(MEDIA_ROOT, gitUsername, fileName)
    ]
    print(file_list)
    commit_message = 'Testing push of {}/{}'.format(gitUsername, fileName)
    repo.index.add(file_list)
    repo.index.commit(commit_message)
    origin = repo.remote('origin')
    origin.pull()
    origin.push()
