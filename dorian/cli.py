import click

from dorian.clone import clone
from dorian.extract import extract
from dorian.write import write


@click.command()
@click.argument("repo_url", required=True)
@click.argument("output_file", required=False, default="dora.csv")
def cli(repo_url, output_file):
    repo_dir = clone(repo_url)
    deployment_times = extract(repo_dir)
    write(deployment_times, output_file)


if __name__ == "__main__":
    cli()
