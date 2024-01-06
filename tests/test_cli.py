import csv
from datetime import datetime, timedelta
from pathlib import Path
from unittest import mock

from click.testing import CliRunner

import dorian.cli as cli
from dorian.git import Git

repo_dir = "./test_repo"


def test_with_no_commits():
    git = Git(repo_dir=repo_dir)
    git.init()

    with mock.patch.object(cli.Git, "clone") as clone:
        clone.return_value = git
        runner = CliRunner()
        result = runner.invoke(cli.cli, ["git@github.com:uttamk/dorian.git"])

    assert result.exit_code == 0
    assert Path('dora.csv').is_file()
    with open(Path('dora.csv')) as f:
        assert list(csv.DictReader(f)) == []


def test_with_one_deployment():
    batch_1_start_time = datetime.now().replace(hour=0, microsecond=0) - timedelta(days=1)
    deploy_1_time = datetime.now().replace(hour=0, microsecond=0)
    git = Git(repo_dir=repo_dir)
    git.init()

    with mock.patch.object(cli.Git, "clone") as clone:
        clone.return_value = git
        git.commit(batch_1_start_time, f"Batch 1 commit 1")
        git.commit(batch_1_start_time + timedelta(hours=1), f"Batch 1 commit 2")
        git.commit(batch_1_start_time + timedelta(hours=2), f"Batch 1 commit 3")
        sha = git.commit(deploy_1_time, f"Batch 1 final commit")
        git.create_tag(_deploy_tag(deploy_1_time), sha)

        runner = CliRunner()
        result = runner.invoke(cli.cli, ["git@github.com:uttamk/dorian.git"])

    assert result.exit_code == 0
    assert Path('dora.csv').is_file()
    with open(Path('dora.csv')) as f:
        assert list(csv.DictReader(f)) == [
            dict(deployment_time=str(deploy_1_time.timestamp()), first_commit_time=''),
        ]


def _deploy_tag(deploy_datetime):
    return f'deploy-{deploy_datetime.strftime("%Y%m%d%H%M%S")}'


def test_with_two_deployments():
    batch_1_start_time = datetime.now().replace(hour=0, microsecond=0) - timedelta(days=1)
    deploy_1_time = datetime.now().replace(hour=0, microsecond=0)
    batch_2_start_time = deploy_1_time + timedelta(hours=1)
    deploy_2_time = datetime.now().replace(hour=0, microsecond=0) + timedelta(days=1)
    git = Git(repo_dir=repo_dir)
    git.init()

    with mock.patch.object(cli.Git, "clone") as clone:
        clone.return_value = git
        git.commit(batch_1_start_time, f"Batch 1 commit 1")
        git.commit(batch_1_start_time + timedelta(hours=1), f"Batch 1 commit 2")
        git.commit(batch_1_start_time + timedelta(hours=2), f"Batch 1 commit 3")
        sha = git.commit(deploy_1_time, f"Batch 1 final commit")
        git.create_tag(_deploy_tag(deploy_1_time), sha)
        git.commit(batch_2_start_time, f"Batch 2 commit 1")
        git.commit(deploy_1_time + timedelta(hours=2), f"Batch 2 commit 2")
        sha = git.commit(deploy_2_time, f"Batch 2 final commit")
        git.create_tag(_deploy_tag(deploy_2_time), sha)

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


def test_with_rollback():
    batch_1_start_time = datetime.now().replace(hour=0, microsecond=0) - timedelta(days=1)
    deploy_1_time = datetime.now().replace(hour=0, microsecond=0)
    batch_2_start_time = deploy_1_time + timedelta(hours=1)
    deploy_2_time = datetime.now().replace(hour=0, microsecond=0) + timedelta(days=1)
    rollback_time = deploy_2_time + timedelta(hours=1)
    batch_3_start_time = rollback_time + timedelta(hours=1)
    deploy_3_time = batch_3_start_time + timedelta(hours=6)
    git = Git(repo_dir=repo_dir)
    git.init()

    with mock.patch.object(cli.Git, "clone") as clone:
        clone.return_value = git
        git.commit(batch_1_start_time, f"Batch 1 commit 1")
        git.commit(batch_1_start_time + timedelta(hours=1), f"Batch 1 commit 2")
        git.commit(batch_1_start_time + timedelta(hours=2), f"Batch 1 commit 3")
        deploy_1_sha = git.commit(deploy_1_time, f"Batch 1 final commit")
        git.create_tag(_deploy_tag(deploy_1_time), deploy_1_sha)
        git.commit(batch_2_start_time, f"Batch 2 commit 1")
        git.commit(deploy_1_time + timedelta(hours=2), f"Batch 2 commit 2")
        sha = git.commit(deploy_2_time, f"Batch 2 final commit")
        git.create_tag(_deploy_tag(deploy_2_time), sha)
        git.create_tag(_deploy_tag(rollback_time), deploy_1_sha)
        git.commit(batch_3_start_time + timedelta(hours=1), f"Batch 3 commit 2")
        sha = git.commit(batch_3_start_time + timedelta(hours=2), f"Batch 3 commit 3")
        git.create_tag(_deploy_tag(deploy_3_time), sha)

        runner = CliRunner()
        result = runner.invoke(cli.cli, ["git@github.com:uttamk/dorian.git"])

    assert result.exit_code == 0
    assert Path('dora.csv').is_file()
    with open(Path('dora.csv')) as f:
        assert list(csv.DictReader(f)) == [
            dict(deployment_time=str(deploy_1_time.timestamp()), first_commit_time=''),
            dict(deployment_time=str(deploy_2_time.timestamp()),
                 first_commit_time=str(batch_2_start_time.timestamp())),
            dict(deployment_time=str(rollback_time.timestamp()),
                 first_commit_time=''),
            dict(deployment_time=str(deploy_3_time.timestamp()),
                 first_commit_time=str(batch_2_start_time.timestamp())),
        ]
