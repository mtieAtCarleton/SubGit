# from https://stackoverflow.com/questions/38594717/how-do-i-push-new-files-to-github
from git import Repo
from SubGit.settings import MEDIA_ROOT

def submit(gitUsername, fileName):
    repo_dir = '/Accounts/bergerg/Desktop/SubGit'
    repo = Repo(repo_dir)
    file_list = [
        '{}/uploads/{}'.format(MEDIA_ROOT, fileName)
    ]
    print(file_list)
    # commit_message = 'Testing push of uploaded file 2'
    # repo.index.add(file_list)
    # repo.index.commit(commit_message)
    # origin = repo.remote('origin')
    # origin.push()
