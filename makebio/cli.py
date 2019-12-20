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
    def __init__(self, debug=False):
        self.root = Path(".")
        self.debug = debug
        self.config = read_config(self.root / "makebio.toml", self.debug)


@click.group()
@click.option("--debug/--no-debug", default=False, help="Print debug information")
@click.pass_context
def cli(ctx, debug):
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
    By default, it marks everything under `data/` to be read-only.

    CONTACT

    Send comments to @raivivek.
    """
    if debug:
        click.echo("Debug mode is on.")

    ctx.obj = Project(debug)

    # Don't throw error if init command is used
    if ctx.obj.config is None and ctx.invoked_subcommand != "init":
        click.echo(
            "fatal: not a makebio configured directory (makebio.toml not found)",
        )
        exit(0)


def read_config(file, debug=False):
    config = None
    if file.exists():
        config = toml.loads(open(file, "r").read())
    return config


def setup_config_and_dir(src, linkto, git, debug):
    src.mkdir(mode=0o744, parents=True)

    # Read template from the directory where this package is installed
    config = read_config(Path(__file__).parent / "config" / "example_config.toml")

    if not config:
        click.echo("Couldn't find template!")
        config = {"params": {}, "configuration": {}, "metadata": {}}

    config["author"] = click.prompt("Author")
    config["email"] = click.prompt("Email")
    config["name"] = src.name

    # [params]
    config["params"]["root"] = str(src.absolute())
    config["params"]["linkto"] = str(linkto.absolute())

    # [configuration]
    config["configuration"]["init_git"] = git
    config["configuration"]["debug"] = debug

    # [metadata]
    config["metadata"]["version"] = __version__
    config["metadata"]["created_on"] = time.strftime("%Y-%m-%d")

    config_path = src / "makebio.toml"

    with open(config_path, "w") as f:
        click.echo(f"Writing configuration to {config_path}")
        toml.dump(config, f)

    (linkto / src.name / "work").mkdir(parents=True, mode=0o744, exist_ok=True)
    (linkto / src.name / "data").mkdir(parents=True, mode=0o744, exist_ok=True)

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
            click.echo("info: git init complete.")
        except Exception as e:
            click.echo("error: failed to init git.")

    click.echo("info: configured.")
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
        click.echo("fatal: directory already exists.")
        exit(0)

    result = click.confirm("Configure project?", default=True)
    if not result:
        exit(0)

    setup_config_and_dir(src, linkto, git, project.debug)


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
        click.echo("info: created %s." % dir_name)
    except FileExistsError as e:
        click.echo("fatal: directories already exist.")
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
        click.echo("info: created %s." % dir_name)
    except FileExistsError as e:
        click.echo("fatal: directories already exist.")
        exit(0)


@cli.command()
@click.argument("path", type=click.Path(exists=True))
@click.pass_obj
def freeze(project, path):
    """Mark a directory read only."""
    # Set read/execute bits
    if Path(path).is_dir():
        chmod(path, S_IREAD | S_IRGRP | S_ISVTX | S_IXUSR | S_IXGRP)
        click.echo("info: directory marked read only.")
    else:
        chmod(path, S_IREAD | S_IRGRP | S_ISVTX)
        click.echo("info: file marked read only.")

    return path


@cli.command()
@click.pass_obj
def save(project):
    """Save a snapshot."""
    try:
        current_date = time.strftime("%Y-%m-%d %H:%M")
        check_output(["git", "add", "-A", "."])
        check_output(["git", "commit", "-s", "-m", f"Snapshot {current_date}"])
        click.echo("info: files added and commited.")
    except Exception as e:
        click.echo("fatal: couldn't save. nothing to save?")
