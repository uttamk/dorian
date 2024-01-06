#### What is Dorian?

Dorian is a command line app that analyses your git repository and outputs the deployment time and the first commit time
for that deploy into a csv file.
It does these by looking at git tags on your repository. For this to work you need to tag git commits
as `deploy-yyyymmddhhmm`. This date needs to be in the UTC timezone.

#### Installation

```shell
pipx install git+https://github.com/uttamk/dorian.git
```

#### Usage

It just needs the repo url to your code repository

```shell
dorian git@github.com:uttamk/dorian-test.git 
```

