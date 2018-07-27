# from https://stackoverflow.com/questions/38594717/how-do-i-push-new-files-to-github
from git import Repo

def submit(gitUsername, fileName):
    repo_dir = '/Accounts/bergerg/Desktop/SubGit'
    repo = Repo(repo_dir)
    file_list = [
        '/Accounts/bergerg/Desktop/SubGit/media/uploads/{}'.format(fileName)
    ]
    print(file_list)
    commit_message = 'Testing push of uploaded file'
    repo.index.add(file_list)
    repo.index.commit(commit_message)
    origin = repo.remote('origin')
    origin.push()
