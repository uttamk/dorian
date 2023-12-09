import csv
import random
import string
from datetime import datetime, timedelta
from functools import reduce
from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from dorian.cli import cli
from dorian.command import run_command

repo_dir = "./test_repo"


def commit_tag(date: datetime) -> str:
    random_file = ''.join(random.choices(string.ascii_uppercase +
                                         string.digits, k=5))
    return f"""
    cd {repo_dir}
    touch {random_file}
    git add {random_file}
    git commit -m 'Add {random_file}'
    git tag deploy-{date.strftime("%Y%m%d%H%M%S")}
    """


def commit_commands(deploy_tag_dates):
    return reduce(lambda cmd, date: "\n".join([cmd, commit_tag(date)]), deploy_tag_dates, "")


def setup_test_repo(deploy_tag_dates: list[datetime]):
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

    for date in deploy_tag_dates:
        run_command(commit_tag(date))


@patch('dorian.cli.clone')
def test_cli(clone):
    today = datetime.now().replace(microsecond=0)
    yesterday = datetime.now().replace(microsecond=0) - timedelta(days=1)

    setup_test_repo(deploy_tag_dates=[today, yesterday])
    runner = CliRunner()
    clone.return_value = repo_dir
    result = runner.invoke(cli, ["git@github.com:uttamk/dorian.git"])

    assert result.exit_code == 0
    assert Path('dora.csv').is_file()
    with open(Path('dora.csv')) as f:
        assert list(csv.DictReader(f)) == [
            dict(deployment_time=str(yesterday.timestamp()), first_commit_time=''),
            dict(deployment_time=str(today.timestamp()), first_commit_time=''),
        ]
