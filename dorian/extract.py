from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class DeploymentTime:
    deployment_time: datetime
    first_commit_time: datetime


def extract(repo_dir: str) -> list[DeploymentTime]:
    return [DeploymentTime(datetime.now(), None)]
