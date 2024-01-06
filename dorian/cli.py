import csv
from dataclasses import dataclass
from datetime import datetime, timezone

import click

from dorian.git import Git


@dataclass
class DeploymentTime:
    deployment_time: datetime
    first_commit_time: datetime


def _deployment_time(tag: str):
    date_str = tag.split("-")[-1]

    return datetime(year=int(date_str[0:4]),
                    month=int(date_str[4:6]),
                    day=int(date_str[6:8]),
                    hour=int(date_str[8:10]),
                    minute=int(date_str[10:12]),
                    second=int(date_str[12:14]), tzinfo=timezone.utc)


def _first_commit_time(idx: int, git: Git, seen_shas: list[str]) -> datetime or None:
    current_deployment_sha = git.rev_parse(git.tags()[idx])
    if idx == 0 or current_deployment_sha in seen_shas:
        seen_shas.append(current_deployment_sha)
        return None
    seen_shas.append(current_deployment_sha)
    prev_deployment_sha = git.rev_parse(git.tags()[idx - 1])
    next_sha = git.next_sha(prev_deployment_sha)
    return git.commit_time(next_sha) if next_sha else None


def extract(git: Git) -> list[DeploymentTime]:
    seen_shas = []
    tags = git.tags()
    tags.sort()
    return [
        DeploymentTime(deployment_time=_deployment_time(tag),
                       first_commit_time=_first_commit_time(idx, git, seen_shas))
        for idx, tag in enumerate(tags)
    ]


def write(deployment_times: list[DeploymentTime], output_file):
    with open(output_file, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['deployment_time', 'first_commit_time'])
        writer.writerows(
            [(dt.deployment_time.timestamp(), dt.first_commit_time.timestamp() if dt.first_commit_time else None) for dt
             in deployment_times])
        click.echo('Metrics written to {}'.format(output_file))


@click.command()
@click.argument("target", required=True)
@click.argument("output_file", required=False, default="dora.csv")
def cli(target, output_file):
    git = Git.clone(target) if ".git" in target else Git(repo_dir=target)
    deployment_times = extract(git)
    write(deployment_times, output_file)


if __name__ == "__main__":
    cli()
