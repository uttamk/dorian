import csv
from datetime import datetime, timedelta
from pathlib import Path
from unittest import mock

from click.testing import CliRunner

import dorian.cli as cli
from dorian.command import run_command
from dorian.git import Git

repo_dir = "./test_repo"


def setup_test_repo():
    run_command(f"""
    rm -rf {repo_dir}
    mkdir -p {repo_dir}
    cd {repo_dir}
    git init
    touch initial_commit.txt
    git add .
    git commit -m "Initial commit"
    git -P log
    git -P tag
    """)


def test_cli():
    today = datetime.now().replace(microsecond=0)
    yesterday = datetime.now().replace(microsecond=0) - timedelta(days=1)
    setup_test_repo()
    git = Git(repo_dir=repo_dir)
    with mock.patch.object(cli.Git, "clone") as clone:
        clone.return_value = git
        for idx, date in enumerate([today, yesterday]):
            sha = git.commit(date, f"Commit {idx}")
            git.create_tag(f'deploy-{date.strftime("%Y%m%d%H%M%S")}', sha)

        runner = CliRunner()
        result = runner.invoke(cli.cli, ["git@github.com:uttamk/dorian.git"])

    assert result.exit_code == 0
    assert Path('dora.csv').is_file()
    with open(Path('dora.csv')) as f:
        assert list(csv.DictReader(f)) == [
            dict(deployment_time=str(yesterday.timestamp()), first_commit_time=''),
            dict(deployment_time=str(today.timestamp()), first_commit_time=''),
        ]
