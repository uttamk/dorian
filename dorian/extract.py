from dataclasses import dataclass
from datetime import datetime, timedelta

from dorian.command import run_command
from dorian.git import Git


@dataclass
class DeploymentTime:
    deployment_time: datetime
    first_commit_time: datetime


def _deployment_dates(tags: list[str]) -> list[datetime]:
    date_strs = [tag.split("-")[-1] for tag in tags]
    return [
        datetime(year=int(date_str[0:4]),
                 month=int(date_str[4:6]),
                 day=int(date_str[6:8]),
                 hour=int(date_str[8:10]),
                 minute=int(date_str[10:12]),
                 second=int(date_str[12:14]))
        for date_str in date_strs
    ]


def extract(git: Git) -> list[DeploymentTime]:
    tags = git.tags()
    deployment_dates = _deployment_dates(tags)
    return [DeploymentTime(date, None) for date in deployment_dates]
