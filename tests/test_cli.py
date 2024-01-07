import csv
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

from click.testing import CliRunner

import dorian.cli as cli
from dorian.git import Git


class TestCli(unittest.TestCase):
    def setUp(self):
        self.repo_dir = "./test_repo"
        self.git = Git(repo_dir=self.repo_dir)
        self.git.init()

    def test_with_no_commits(self):
        with mock.patch.object(cli.Git, "clone") as clone:
            clone.return_value = self.git
            runner = CliRunner()
            result = runner.invoke(cli.cli, [self.repo_dir])

        assert result.exit_code == 0
        assert Path('dora.csv').is_file()
        with open(Path('dora.csv')) as f:
            assert list(csv.DictReader(f)) == []

    def test_with_one_deployment_with_repo_url(self):
        batch_1_start_time = datetime.now().replace(hour=0, microsecond=0) - timedelta(days=1)
        deploy_1_time = datetime.now().replace(hour=0, microsecond=0)

        with mock.patch.object(cli.Git, "clone") as clone:
            clone.return_value = self.git
            self.git.commit(batch_1_start_time, f"Batch 1 commit 1")
            self.git.commit(batch_1_start_time + timedelta(hours=1), f"Batch 1 commit 2")
            self.git.commit(batch_1_start_time + timedelta(hours=2), f"Batch 1 commit 3")
            deploy_sha = self.git.commit(deploy_1_time, f"Batch 1 final commit")
            self.git.create_tag(self._deploy_tag(deploy_1_time), deploy_sha)

            repo_url = "git@github.com:uttamk/dorian.git"
            runner = CliRunner()
            result = runner.invoke(cli.cli, [repo_url])
            clone.assert_called_once_with(repo_url)

        assert result.exit_code == 0
        assert Path('dora.csv').is_file()
        with open(Path('dora.csv')) as f:
            assert list(csv.DictReader(f)) == [
                dict(
                    deployment_timestamp=str(deploy_1_time.timestamp()),
                    first_commit_timestamp='',
                    deploy_sha=deploy_sha,
                    first_commit_sha=''
                ),
            ]

    def test_with_one_deployment(self):
        batch_1_start_time = datetime.now().replace(hour=0, microsecond=0) - timedelta(days=1)
        deploy_1_time = datetime.now().replace(hour=0, microsecond=0)

        self.git.commit(batch_1_start_time, f"Batch 1 commit 1")
        self.git.commit(batch_1_start_time + timedelta(hours=1), f"Batch 1 commit 2")
        self.git.commit(batch_1_start_time + timedelta(hours=2), f"Batch 1 commit 3")
        deploy_sha = self.git.commit(deploy_1_time, f"Batch 1 final commit")
        self.git.create_tag(self._deploy_tag(deploy_1_time), deploy_sha)

        runner = CliRunner()
        result = runner.invoke(cli.cli, [self.repo_dir])

        assert result.exit_code == 0
        assert Path('dora.csv').is_file()
        with open(Path('dora.csv')) as f:
            assert list(csv.DictReader(f)) == [
                dict(
                    deployment_timestamp=str(deploy_1_time.timestamp()),
                    first_commit_timestamp='',
                    deploy_sha=deploy_sha,
                    first_commit_sha=''
                ),
            ]

    def test_with_two_deployments(self):
        batch_1_start_time = datetime.now().replace(hour=0, microsecond=0) - timedelta(days=1)
        deploy_1_time = datetime.now().replace(hour=0, microsecond=0)
        batch_2_start_time = deploy_1_time + timedelta(hours=1)
        deploy_2_time = datetime.now().replace(hour=0, microsecond=0) + timedelta(days=1)

        self.git.commit(batch_1_start_time, f"Batch 1 commit 1")
        self.git.commit(batch_1_start_time + timedelta(hours=1), f"Batch 1 commit 2")
        self.git.commit(batch_1_start_time + timedelta(hours=2), f"Batch 1 commit 3")
        deploy_1_sha = self.git.commit(deploy_1_time, f"Batch 1 final commit")
        self.git.create_tag(self._deploy_tag(deploy_1_time), deploy_1_sha)
        first_commit_sha = self.git.commit(batch_2_start_time, f"Batch 2 commit 1")
        self.git.commit(deploy_1_time + timedelta(hours=2), f"Batch 2 commit 2")
        deploy_2_sha = self.git.commit(deploy_2_time, f"Batch 2 final commit")
        self.git.create_tag(self._deploy_tag(deploy_2_time), deploy_2_sha)

        runner = CliRunner()
        result = runner.invoke(cli.cli, [self.repo_dir])

        assert result.exit_code == 0
        assert Path('dora.csv').is_file()
        with open(Path('dora.csv')) as f:
            assert list(csv.DictReader(f)) == [
                dict(
                    deployment_timestamp=str(deploy_1_time.timestamp()),
                    first_commit_timestamp='',
                    first_commit_sha='',
                    deploy_sha=deploy_1_sha
                ),
                dict(
                    deployment_timestamp=str(deploy_2_time.timestamp()),
                    first_commit_timestamp=str(batch_2_start_time.timestamp()),
                    deploy_sha=deploy_2_sha,
                    first_commit_sha=first_commit_sha
                ),
            ]

    def test_with_rollback(self):
        batch_1_start_time = datetime.now().replace(hour=0, microsecond=0) - timedelta(days=1)
        deploy_1_time = datetime.now().replace(hour=0, microsecond=0)
        batch_2_start_time = deploy_1_time + timedelta(hours=1)
        deploy_2_time = datetime.now().replace(hour=0, microsecond=0) + timedelta(days=1)
        rollback_time = deploy_2_time + timedelta(hours=1)
        batch_3_start_time = rollback_time + timedelta(hours=1)
        deploy_3_time = batch_3_start_time + timedelta(hours=6)

        self.git.commit(batch_1_start_time, f"Batch 1 commit 1")
        self.git.commit(batch_1_start_time + timedelta(hours=1), f"Batch 1 commit 2")
        self.git.commit(batch_1_start_time + timedelta(hours=2), f"Batch 1 commit 3")
        deploy_1_sha = self.git.commit(deploy_1_time, f"Batch 1 final commit")
        self.git.create_tag(self._deploy_tag(deploy_1_time), deploy_1_sha)
        batch_2_first_sha = self.git.commit(batch_2_start_time, f"Batch 2 commit 1")
        self.git.commit(deploy_1_time + timedelta(hours=2), f"Batch 2 commit 2")
        deploy_2_sha = self.git.commit(deploy_2_time, f"Batch 2 final commit")
        self.git.create_tag(self._deploy_tag(deploy_2_time), deploy_2_sha)
        self.git.create_tag(self._deploy_tag(rollback_time), deploy_1_sha)
        self.git.commit(batch_3_start_time + timedelta(hours=1), f"Batch 3 commit 1")
        deploy_3_sha = self.git.commit(batch_3_start_time + timedelta(hours=2), f"Batch 3 commit 1")
        self.git.create_tag(self._deploy_tag(deploy_3_time), deploy_3_sha)

        runner = CliRunner()
        result = runner.invoke(cli.cli, [self.repo_dir])

        assert result.exit_code == 0
        assert Path('dora.csv').is_file()
        with open(Path('dora.csv')) as f:
            assert list(csv.DictReader(f)) == [
                dict(deployment_timestamp=str(deploy_1_time.timestamp()),
                     first_commit_timestamp='',
                     first_commit_sha='',
                     deploy_sha=deploy_1_sha),
                dict(deployment_timestamp=str(deploy_2_time.timestamp()),
                     first_commit_timestamp=str(batch_2_start_time.timestamp()),
                     first_commit_sha=batch_2_first_sha,
                     deploy_sha=deploy_2_sha),
                dict(deployment_timestamp=str(rollback_time.timestamp()),
                     first_commit_timestamp='',
                     first_commit_sha='',
                     deploy_sha=deploy_1_sha),
                dict(deployment_timestamp=str(deploy_3_time.timestamp()),
                     first_commit_timestamp=str(batch_2_start_time.timestamp()),
                     first_commit_sha=batch_2_first_sha,
                     deploy_sha=deploy_3_sha),
            ]

    @staticmethod
    def _deploy_tag(deploy_datetime):
        return f'deploy-{deploy_datetime.astimezone(timezone.utc).strftime("%Y%m%d%H%M%S")}'
