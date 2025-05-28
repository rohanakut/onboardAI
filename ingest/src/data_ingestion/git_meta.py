# git_meta.py
from git import Repo
from constants import *

repo = Repo(repo_path)

def get_file_meta(path):
    """Return author and date for the most recent commit touching this file."""
    commits = list(repo.iter_commits(paths=path, max_count=1))
    if not commits:
        return {}
    c = commits[0]
    return {
        "author": c.author.name,
        "email": c.author.email,
        "date": c.committed_datetime.isoformat(),
        "sha": c.hexsha
    }

if __name__ == "__main__":
    example = get_file_meta("django/core/management/base.py")
    print(example)
