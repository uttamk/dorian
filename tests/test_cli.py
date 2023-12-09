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
    """)


def test_cli():
    batch_1_start_time = datetime.now().replace(hour=0, microsecond=0) - timedelta(days=1)
    deploy_1_time = datetime.now().replace(hour=0, microsecond=0)
    batch_2_start_time = deploy_1_time + timedelta(hours=1)
    deploy_2_time = datetime.now().replace(hour=0, microsecond=0) + timedelta(days=1)
    setup_test_repo()

    git = Git(repo_dir=repo_dir)
    with mock.patch.object(cli.Git, "clone") as clone:
        clone.return_value = git
        git.commit(batch_1_start_time, f"Batch 1 commit 1")
        git.commit(batch_1_start_time + timedelta(hours=1), f"Batch 1 commit 2")
        git.commit(batch_1_start_time + timedelta(hours=2), f"Batch 1 commit 3")
        sha = git.commit(deploy_1_time, f"Batch 1 final commit")
        git.create_tag(f'deploy-{deploy_1_time.strftime("%Y%m%d%H%M%S")}', sha)
        git.commit(batch_2_start_time, f"Batch 2 commit 1")
        git.commit(deploy_1_time + timedelta(hours=2), f"Batch 2 commit 2")
        sha = git.commit(deploy_2_time, f"Batch 2 final commit")
        git.create_tag(f'deploy-{deploy_2_time.strftime("%Y%m%d%H%M%S")}', sha)

        runner = CliRunner()
        result = runner.invoke(cli.cli, ["git@github.com:uttamk/dorian.git"])

    assert result.exit_code == 0
    assert Path('dora.csv').is_file()
    with open(Path('dora.csv')) as f:
        assert list(csv.DictReader(f)) == [
            dict(deployment_time=str(deploy_1_time.timestamp()), first_commit_time=''),
            dict(deployment_time=str(deploy_2_time.timestamp()),
                 first_commit_time=str(batch_2_start_time.timestamp())),
        ]
