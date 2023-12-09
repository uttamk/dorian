import string
from dataclasses import dataclass
from datetime import datetime
import random

from dorian.command import run_command


@dataclass
class Git(object):
    repo_dir: str

    def commit(self, date: datetime, message: str) -> str:
        random_file = ''.join(random.choices(string.ascii_uppercase +
                                             string.digits, k=5))
        formatted_date = date.strftime("%c")
        run_command(f"""
        export GIT_COMMITTER_DATE='{formatted_date}'
        cd {self.repo_dir}
        touch {random_file}
        git add {random_file}
        git commit -m '{message}' --date='{formatted_date}'
        """)

        return run_command(f"""cd {self.repo_dir}
                           git rev-parse HEAD""")

    def create_tag(self, tag_name, sha) -> str:
        return run_command(f"""
        cd {self.repo_dir}
        git -P log {sha}
        git tag {tag_name} {sha}
        """)

    def tags(self) -> list[str]:
        return run_command(f"""cd {self.repo_dir}
        git -P tag
        """).splitlines()

    def rev_parse(self, ref: str):
        return run_command(f"""cd {self.repo_dir}
        git rev-parse {ref}""")

    def next_sha(self, prev_sha: str):
        return run_command(f"""cd {self.repo_dir}
            git rev-list {prev_sha}..HEAD --reverse
        """).splitlines()[0]

    def commit_time(self, sha: str):
        date_str = run_command(f"""cd {self.repo_dir}
         git -P show --no-patch --format=%ci {sha}""")
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S %z")

    @classmethod
    def clone(cls, url: str, repo_dir: str = "."):
        return Git(repo_dir=repo_dir)
