import string
import subprocess
from dataclasses import dataclass
from datetime import datetime
import random
from pathlib import Path


@dataclass
class Git(object):
    repo_dir: str

    def init(self):
        return _run_command(f"""
        set -e
        rm -rf {self.repo_dir}
        mkdir -p {self.repo_dir}
        cd {self.repo_dir}
        git init
        """)

    def commit(self, date: datetime, message: str) -> str:
        random_file = ''.join(random.choices(string.ascii_uppercase +
                                             string.digits, k=5))
        formatted_date = date.strftime("%c")
        _run_command(f"""
        export GIT_COMMITTER_DATE='{formatted_date}'
        cd {self.repo_dir}
        touch {random_file}
        git add {random_file}
        git commit -m '{message}' --date='{formatted_date}'
        """)

        return _run_command(f"""cd {self.repo_dir}
                           git rev-parse HEAD""")

    def create_tag(self, tag_name, sha) -> str:
        return _run_command(f"""
        cd {self.repo_dir}
        git -P log {sha}
        git tag {tag_name} {sha}
        """)

    def tags(self) -> list[str]:
        return _run_command(f"""cd {self.repo_dir}
        git -P tag
        """).splitlines()

    def rev_parse(self, ref: str):
        return _run_command(f"""cd {self.repo_dir}
        git rev-parse {ref}""")

    def next_sha(self, prev_sha: str) -> str or None:
        result = _run_command(f"""cd {self.repo_dir}
            git rev-list {prev_sha}..HEAD --reverse
        """).splitlines()
        return result[0] if result else None

    def commit_time(self, sha: str):
        date_str = _run_command(f"""cd {self.repo_dir}
         git -P show --no-patch --format=%ai {sha}""")
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S %z")


def _run_command(cmd: str):
    cmd = f"""set -e; {cmd}"""
    return (subprocess
            .check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode()).strip(" \n")
