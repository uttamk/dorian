from pathlib import Path
import csv

from dorian.extract import DeploymentTime


def write(deployment_times: list[DeploymentTime], output_file):
    with open(output_file, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['Deployment Time', 'First commit time'])
        writer.writerows([(dt.deployment_time, dt.first_commit_time) for dt in deployment_times])
