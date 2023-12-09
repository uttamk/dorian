from dorian.git import Git


def clone(repo_url: str) -> Git:
    return Git(".")
