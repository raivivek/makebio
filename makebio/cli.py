# -*- coding: utf-8 -*-

import time
from os import chmod
from pathlib import Path
from shutil import copyfile
from stat import S_IREAD, S_IRGRP, S_ISVTX, S_IXGRP, S_IXUSR
from subprocess import check_output, Popen

import click
import toml

from .about import __version__


class Project(object):
    def __init__(self, path="."):
        self._config = {
            "author": "",
            "email": "",
            "name": "",
            "params": {
                "root": Path(path).absolute(),
                "linkto": ""
            },
            "configuration": {
                "init_git": ""
            },
            "metadata": {
                "version": __version__,
                "created_on": "",
                "last_commit": ""
            },
        }

    @property
    def config(self):
        config_p = Path(self._config["params"]["root"]) / "makebio.toml"
        flag = False
        if config_p.exists():
            flag = True
            self._config = toml.loads(open(config_p, "r").read())
        return (self._config, flag)

    @config.setter
    def config(self, config):
        config_p = Path(self._config["params"]["root"]) / "makebio.toml"
        with open(config_p, "w") as f:
            toml.dump(config, f)
            click.echo("info: wrote config to %s." % config_p)
        return True


@click.group()
@click.version_option(version=__version__)
@click.pass_context
def cli(ctx):
    """Manage computational biology research projects.

    Computational biology or Bioinformatics projects utilize HPC systems that
    typically limit the amount of space on your home directory and provide an
    external mounted space for scratch work. The idea is that your code and
    necessary files sit within the home directory and all intermediate files
    which could take up a lot of space are kept on the scratch.

    This necessitates organizing your work in such a way that even though the
    underlying data is fragmented, it all should transparently appear in one
    place for the user.

    makebio is a simple utility to create and manage such projects. While still
    in development, it is actively used by at least one person in their daily
    bioinformatics work.

    NOTES

    `analysis` and `data` directories are prefixed with the date of creation.
    For example, `2019-04-20_createTracks` or `2019-05-01_fastq`.

    `freeze` marks the target directory and all files within to be read-only.

    CONTACT

    Please leave suggestions on and bugs reports on GitHub [1].\n

    [1]: https://github.com/raivivek/makebio\n
    @raivivek
    """
    ctx.obj = Project()

    # Don't throw error if init command is used
    if not ctx.obj.config[1] and ctx.invoked_subcommand != "init":
        click.secho(
            "fatal: not a makebio configured directory (makebio.toml not found)",
            fg="red",
        )
        click.echo("info: makebio --help.")
        exit(0)


def setup_config_and_dir(project, src, linkto, git):
    config, config_found_flag = project.config

    if config_found_flag:
        return config

    config["author"] = click.prompt("author", default="Vivek Rai")
    config["email"] = click.prompt("email", default="vivekrai@umich.edu")

    # [params]
    config["name"] = src.name
    config["params"]["root"] = str(src.absolute())
    config["params"]["linkto"] = str(linkto.absolute())

    # [configuration]
    config["configuration"]["init_git"] = git

    # [metadata]
    config["metadata"]["version"] = __version__
    config["metadata"]["created_on"] = time.strftime("%Y-%m-%d")
    config["metadata"]["last_commit"] = "null"

    (linkto / src.name / "work").mkdir(parents=True)
    (linkto / src.name / "data").mkdir(parents=True)

    src.mkdir(mode=0o744, parents=True)

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
            check_output(f"git init {src}", shell=True)
            click.secho("info: git init complete.", fg="yellow")
        except Exception:
            click.secho("error: failed to init git.", fg="red")

    project.config = config

    click.secho("info: done.", fg="green")
    return config


@cli.command()
@click.argument("src", type=click.Path())
@click.argument("linkto", type=click.Path())
@click.option("--git/--no-git", default=True)
@click.pass_obj
def init(project, src, linkto, git):
    """Initialize a new project.

    Sets up the directory structure, and if specified by --git, also puts
    the whole directory under Git (if installed) version control. Suitable
    .gitignore is also supplied.
    """
    src, linkto = Path(src).expanduser(), Path(linkto).expanduser()
    if src.exists():
        click.secho("fatal: %s already exists." % src, fg="red")
        exit(0)

    if (linkto / src.name).exists():
        click.secho("fatal: %s already exists." % (linkto / src.name), fg="red")
        exit(0)

    result = click.confirm("configure project?", default=True)
    if not result:
        click.secho("OK.")
        exit(0)

    setup_config_and_dir(project, src, linkto, git)


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
    root = Path(project.config[0]["params"]["root"])

    try:
        dir_name = f"{prefix}{name}"
        (root / "control" / dir_name).mkdir(parents=True)
        (root / "work" / dir_name).mkdir(parents=True)
        # `target_is_directory` must be True for compatibility with Windows
        (root / "control" / dir_name / "work").symlink_to(root / "work" / dir_name, target_is_directory=True)

        click.secho("success: created %s." % dir_name, fg="green")
    except FileExistsError as e:
        click.secho("fatal: directories already exist -- %s" % str(e), fg="red")
        exit(1)


@cli.command()
@click.pass_obj
@click.option("-a", "--all", is_flag=True)
@click.option("-l", "--latest", default=True, is_flag=True)
def show(project, all, latest):
    """Show current configuration."""

    if all:
        print(toml.dumps(project.config[0]))

    if latest:
        proc = Popen(["git", "log", "-1"], shell=False)
        proc.communicate()

    exit(0)


@cli.command()
@click.pass_obj
def update(project):
    """Refresh configuration with new changes.

    If you manually save your working tree, the commit information can become
    out of sync with the value saved in `makebio.toml`. This command will
    update recorded value with last commit in the tree.
    """

    last_recorded_commit = project.config[0]["metadata"]["last_commit"]

    if last_recorded_commit == "null":
        click.secho("info: please run `makebio save` first.", fg="yellow")
        exit(0)

    current_head = check_output("git rev-parse HEAD", shell=True, encoding="utf-8").strip()

    if current_head != last_recorded_commit:
        update_info, _ = project.config
        update_info["metadata"].update({"last_commit": current_head})
        click.secho("info: updating last recorded commit to current HEAD.", fg="yellow")
        project.config = update_info
    else:
        click.secho("success: nothing to update.", fg="green")
        exit(0)

    pass

@cli.command()
@click.argument("old")
@click.argument("new")
@click.option("--dry-run", is_flag=True)
@click.pass_obj
def rename_analysis(project, old, new, dry_run):
    """Rename existing analysis."""

    root = Path(project.config[0]["params"]["root"])
    old_analysis_path = (root / "control" / old)
    new_analysis_path = (root / "control" / new)

    if not old_analysis_path.exists():
        click.secho("fatal: analysis directory not found -- %s" % str(old), fg="red")
        exit(1)

    if new_analysis_path.exists():
        click.secho("fatal: target anlaysis directory already exists", fg="red")
        exit(1)

    if dry_run:
        click.secho("info: will rename following directorie(s)", fg="green")
        click.secho("%s --> %s" % (str(old_analysis_path), str(new_analysis_path)), fg="yellow")
        click.secho("%s --> %s" % (str(root / "work" / old), str(root / "work" / new)), fg="yellow")

        click.secho("info: will update following symlink(s) ", fg="green")
        click.secho("%s --> %s" % (str(old_analysis_path / "work"), str(root / "work" / new)), fg="yellow")
        exit(0)

    try:
        new_analysis_path = old_analysis_path.rename(root / "control" / new)
        new_work_path = (root / "work" / old).rename(root / "work" / new)

        (new_analysis_path / "tmp").symlink_to(new_work_path, target_is_directory=True)
        (new_analysis_path / "tmp").replace(new_analysis_path / "work")
        click.secho("success: renamed %s --> %s." % (old, new), fg="green")
    except FileExistsError as e:
        click.secho("fatal: directories already exist -- %s" % str(e), fg="red")
        exit(1)


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
    root = Path(project.config[0]["params"]["root"])

    try:
        dir_name = f"{prefix}{name}"
        (root / "control" / dir_name).mkdir(parents=True)
        (root / "data" / dir_name).mkdir(parents=True)
        click.secho("success: created %s." % dir_name, fg="green")
    except FileExistsError as e:
        click.secho("fatal: directories already exist -- %s" % str(e), fg="red")
        exit(1)


@cli.command()
@click.argument("path", type=click.Path(exists=True))
@click.argument("--recursive", required=False, default=False)
@click.pass_obj
def freeze(project, path, recursive):
    """Mark a directory/file read only (for the user/group).

    Sets the sticky bit so that only owner can change the persmissions.

    --recursive will make all dirs/files within readonly.
    """
    if Path(path).is_dir():
        chmod(
            path, S_IREAD | S_IRGRP | S_ISVTX | S_IXUSR | S_IXGRP
        )  # Set read/execute bits
        click.secho("success: directory marked read only.", fg="green")
    else:
        chmod(path, S_IREAD | S_IRGRP | S_ISVTX)
        click.secho("success: file marked read only.", fg="green")

    return path


@cli.command()
@click.argument("path", type=click.Path(exists=True), required=False)
@click.pass_obj
def save(project, path):
    """Save a (Git) snapshot.

    Stage all files and commit them. No Undo command is implemented, so
    if you commit all the changes, just write a new commit to make new
    changes (including reverts).
    """
    if path:
        project
    try:
        check_if_git = check_output("git rev-parse --is-inside-work-tree", shell=True, encoding="utf-8").strip()
        # Initialize git if not done before
        if not check_if_git == "true":
            check_output("git init", shell=True)
            click.secho("info: initialized git")

        check_untracked = check_output("git status -s", shell=True).strip().split()

        if len(check_untracked) < 2:
            click.secho("tip: nothing to save?")
            return

        current_date = time.strftime("%Y-%m-%d %H:%M")
        check_output("git ls-files -z -dmo --exclude-standard | xargs -0 git add", shell=True)
        check_output(f"git commit -m \"{current_date}\"", shell=True)
        click.secho("success: files added and committed.", fg="green")

        commit_id = check_output("git rev-parse HEAD", shell=True, encoding="utf-8").strip()

        update_info, _ = project.config
        update_info["metadata"].update({"last_commit": commit_id})
        project.config = update_info
    except Exception as e:
        click.secho("fatal: couldn't save -- %s" % str(e), fg="red")
        click.echo("tip: nothing to commit?")
        exit(0)
