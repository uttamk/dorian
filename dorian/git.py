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
        run_command(f"""
        cd {self.repo_dir}
        touch {random_file}
        git add {random_file}
        git commit -m 'Add {random_file}'
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

    @classmethod
    def clone(cls, url: str, repo_dir: str = "."):
        return Git(repo_dir=repo_dir)
