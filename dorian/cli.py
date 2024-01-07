import csv
from dataclasses import dataclass
from datetime import datetime, timezone

import click

from dorian.git import Git


@dataclass
class DeploymentTime:
    deployment_timestamp: datetime
    first_commit_timestamp: datetime
    first_commit_sha: str
    deploy_sha: str


def _deployment_time(tag: str):
    date_str = tag.split("-")[-1]

    return datetime(year=int(date_str[0:4]),
                    month=int(date_str[4:6]),
                    day=int(date_str[6:8]),
                    hour=int(date_str[8:10]),
                    minute=int(date_str[10:12]),
                    second=int(date_str[12:14]), tzinfo=timezone.utc)


def _first_commit_data(idx: int, git: Git, seen_shas: list[str]) -> tuple[datetime, str] or None:
    current_deployment_sha = git.rev_parse(git.tags()[idx])
    if idx == 0 or current_deployment_sha in seen_shas:
        seen_shas.append(current_deployment_sha)
        return None, None
    seen_shas.append(current_deployment_sha)
    prev_deployment_sha = git.rev_parse(git.tags()[idx - 1])
    next_sha = git.next_sha(prev_deployment_sha)
    return (git.commit_time(next_sha), next_sha) if next_sha else (None, None)


def _commit_sha(git: Git, tag: str) -> str:
    return git.rev_parse(tag)


def extract(git: Git) -> list[DeploymentTime]:
    seen_shas = []
    tags = git.tags()
    tags.sort()
    deployment_times = []
    for idx, tag in enumerate(tags):
        first_commit_time, first_commit_sha = _first_commit_data(idx, git, seen_shas)
        deployment_times.append(DeploymentTime(deployment_timestamp=_deployment_time(tag),
                                               deploy_sha=_commit_sha(git, tag),
                                               first_commit_sha=first_commit_sha,
                                               first_commit_timestamp=first_commit_time))
    return deployment_times


def write(deployment_times: list[DeploymentTime], output_file):
    with open(output_file, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['deployment_timestamp', 'first_commit_timestamp', 'deploy_sha', 'first_commit_sha'])
        writer.writerows(
            [
                (
                    dt.deployment_timestamp.timestamp(),
                    dt.first_commit_timestamp.timestamp() if dt.first_commit_timestamp else None,
                    dt.deploy_sha,
                    dt.first_commit_sha,
                ) for dt in deployment_times
            ]
        )
        click.echo('Metrics written to {}'.format(output_file))


@click.command(help="""Analyse a git repo (target) for deployment times and first commits

                REPO_DIR is a git repo directory

                OUTPUT_FILE is optional. It is dora.csv by default""")
@click.argument("repo_dir", required=True)
@click.argument("output_file", required=False, default="dora.csv")
def cli(repo_dir, output_file):
    git = Git(repo_dir=repo_dir)
    deployment_times = extract(git)
    write(deployment_times, output_file)


if __name__ == "__main__":
    cli()
