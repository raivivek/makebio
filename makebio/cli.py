# -*- coding: utf-8 -*-

import toml
import time
from os import chmod
from pathlib import Path
from shutil import copyfile
from subprocess import check_output
from stat import S_IREAD, S_IRGRP, S_IXUSR, S_IXGRP, S_ISVTX

import click

from .about import __version__


class Project(object):
    def __init__(self):
        self.root = Path(".")
        self.config = read_config(self.root / "makebio.toml")


@click.group()
@click.pass_context
def cli(ctx):
    """Quickly setup research projects.

    Generally, any high-performance computing cluster will limit the amount
    of space on your home directory and provide an external mouted space for
    scratch work. The idea is that your code and necessary files sit within
    the home directory and all intermediate files which could take up a lot
    of space are kept on the scratch.

    This necessiates organizing your work in such a way that even though the
    underlying data is fragmented, it all should transparently appear in one
    place for the user.

    NOTES

    `analysis` and `data` directories are prefixed with the date of creation.
    For example, 2019-04-20_createTracks or 2019-05-01_fastq.

    `freeze` marks the target directory and all files within to be read-only.

    CONTACT

    Find out more at https://github.com/raivivek/makebio
    @raivivek
    """
    ctx.obj = Project()

    # Don't throw error if init command is used
    if ctx.obj.config is None and ctx.invoked_subcommand != "init":
        click.secho(
            "fatal: not a makebio configured directory (makebio.toml not found)",
            fg='red'
        )
        exit(0)


def read_config(file):
    config = None
    if file.exists():
        config = toml.loads(open(file, "r").read())
    return config


def setup_config_and_dir(src, linkto, git):
    # Read template from the directory where this package is installed
    config = read_config(Path(__file__).parent / "config" / "example_config.toml")

    if not config:
        click.secho("warning: could not locate template.", fg='yellow')
        config = {"params": {}, "configuration": {}, "metadata": {}}

    config["author"] = click.prompt("author")
    config["email"] = click.prompt("email")
    config["name"] = src.name

    # [params]
    config["params"]["root"] = str(src.absolute())
    config["params"]["linkto"] = str(linkto.absolute())

    # [configuration]
    config["configuration"]["init_git"] = git

    # [metadata]
    config["metadata"]["version"] = __version__
    config["metadata"]["created_on"] = time.strftime("%Y-%m-%d")

    config_path = src / "makebio.toml"

    try:
        (linkto / src.name / "work").mkdir(parents=True)
        (linkto / src.name / "data").mkdir(parents=True)
    except FileExistsError:
        click.secho("fatal: %s already exists." % (linkto / src.name), fg='red')
        exit(0)

    src.mkdir(mode=0o744, parents=True)

    with open(config_path, "w") as f:
        click.secho(f"info: writing configuration to {config_path}", fg='yellow')
        toml.dump(config, f)

    (src / "control").mkdir()
    (src / "notebooks").mkdir()
    (src / "bin").mkdir()
    (src / "src").mkdir()
    (src / "work").symlink_to(linkto / src.name / "work")
    (src / "data").symlink_to(linkto / src.name / "data")

    if git:
        # Copy gitignore
        copyfile(Path(__file__).parent / "config" / "gitignore", src / ".gitignore")
        try:
            check_output(["git", "init", src])
            click.secho("info: git init complete.", fg='yellow')
        except Exception:
            click.secho("error: failed to init git.", fg='red')

    click.secho("info: done.", fg='green')
    return config


@cli.command()
@click.argument("src", type=click.Path())
@click.argument("linkto", type=click.Path())
@click.option("--git/--no-git", default=True)
@click.pass_obj
def init(project, src, linkto, git):
    """Initialize a new project.

    Sets up the directory structure, and if specified by --git, also puts the whole
    directory under Git (if installed) version control. Suitable .gitignore is also
    supplied.
    """
    src, linkto = Path(src).expanduser(), Path(linkto).expanduser()
    if src.exists():
        click.secho("fatal: %s already exists." % src, fg='red')
        exit(0)

    result = click.confirm("configure project?", default=True)
    if not result:
        exit(0)

    setup_config_and_dir(src, linkto, git)


@cli.command()
@click.argument("name")
@click.option("--prefix/--no-prefix", default=True)
@click.pass_obj
def add_analysis(project, name, prefix):
    """Add new analysis.

    NEW directories will be created in control/ and work/ with the today's
    date as PREFIX (YY-MM-DD): PREFIX_NAME
    """

    prefix = f"{time.strftime('%Y-%m-%d')}_" if prefix else ""
    root = Path(project.config["params"]["root"])

    try:
        dir_name = f"{prefix}{name}"
        (root / "control" / dir_name).mkdir(parents=True)
        (root / "work" / dir_name).mkdir(parents=True)
        click.secho("info: created %s." % dir_name, fg='green')
    except FileExistsError as e:
        click.secho("fatal: directories already exist -- %s" % str(e), fg='red')
        exit(0)


@cli.command()
@click.argument("name")
@click.option("--prefix/--no-prefix", default=True)
@click.pass_obj
def add_data(project, name, prefix):
    """Add new data.

    NEW directories will be created in control/ and data/ with the today's
    date as PREFIX (YY-MM-DD): PREFIX_NAME
    """
    prefix = f"{time.strftime('%Y-%m-%d')}_" if prefix else ""

    root = Path(project.config["params"]["root"])

    try:
        dir_name = f"{prefix}{name}"
        (root / "control" / dir_name).mkdir(parents=True)
        (root / "data" / dir_name).mkdir(parents=True)
        click.secho("info: created %s." % dir_name, fg='green')
    except FileExistsError as e:
        click.secho("fatal: directories already exist -- %s" % str(e), fg='red')
        exit(0)


@cli.command()
@click.argument("path", type=click.Path(exists=True))
@click.pass_obj
def freeze(project, path):
    """Mark a directory/file read only.
    
    Also sets the sticky bit so that only owner can change the persmissions.
    """
    if Path(path).is_dir():
        chmod(path, S_IREAD | S_IRGRP | S_ISVTX | S_IXUSR | S_IXGRP) # Set read/execute bits
        click.secho("info: directory marked read only.", fg='green')
    else:
        chmod(path, S_IREAD | S_IRGRP | S_ISVTX)
        click.secho("info: file marked read only.", fg='green')

    return path


@cli.command()
@click.pass_obj
def save(project):
    """Save a snapshot.
    
    Add all files to staging area and commit them.
    """
    try:
        current_date = time.strftime("%Y-%m-%d %H:%M")
        check_output(["git", "add", "-A", "."])
        check_output(["git", "commit", "-s", "-m", f"Snapshot {current_date}"])
        click.secho("info: files added and commited.", fg='green')
    except Exception as e:
        click.secho("fatal: couldn't save -- %s" % str(e), fg='red')
