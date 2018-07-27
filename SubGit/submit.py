# from https://stackoverflow.com/questions/38594717/how-do-i-push-new-files-to-github
from git import Repo

repo_dir = '/Accounts/bergerg/Desktop/SubGit'
repo = Repo(repo_dir)
file_list = [
    'SubGit/submit.py'
]
commit_message = 'Test GitPython commit/push'
repo.index.add(file_list)
#repo.index.commit(commit_message)
origin = repo.remote('origin')
#origin.push()
