from pathlib import Path
import csv

from dorian.extract import DeploymentTime


def write(deployment_times: list[DeploymentTime], output_file):
    with open(output_file, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['deployment_time', 'first_commit_time'])
        writer.writerows([(dt.deployment_time.timestamp(), None) for dt in deployment_times])
