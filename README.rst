makebio
-------
Manage computational biology projects with ease.

Installation
------------

:code:`pip install makebio`

For autocompletion, add the following lines to your login file (BASH):
::
  eval "$(_MAKEBIO_COMPLETE=source makebio)"


Or for ZSH,
::
    eval "$(_MAKEBIO_COMPLETE=source_zsh makebio)"
    
Usage
-----

See :code:`makebio --help`.

.. code-block::

  Usage: makebio [OPTIONS] COMMAND [ARGS]...

    Manage computational biology research projects.

    Computational biology or Bioinformatics projects utilize HPC systems that
    typically limit the amount of space on your home directory and provide an
    external mounted space for scratch work. The idea is that your code and
    necessary files sit within the home directory and all intermediate files
    which could take up a lot of space are kept on the scratch.

    This necessitates organizing your work in such a way that even though the
    underlying data is fragmented, it all should transparently appear in one
    place for the user.

    makebio is a simple utility to create and manage such projects. While
    still in development, it is actively used by at least one person in their
    daily bioinformatics work.

    NOTES

    `analysis` and `data` directories are prefixed with the date of creation.
    For example, `2019-04-20_createTracks` or `2019-05-01_fastq`.

    `freeze` marks the target directory and all files within to be read-only.

    CONTACT

    Please leave suggestions on and bugs reports on GitHub [1].

    [1]: https://github.com/raivivek/makebio

    @raivivek

  Options:
    --version  Show the version and exit.
    --help     Show this message and exit.

  Commands:
    add-analysis     Add new analysis.
    add-data         Add new data.
    freeze           Mark a directory/file read only (for the user/group).
    init             Initialize a new project.
    rename-analysis  Rename existing analysis.
    save             Save a (Git) snapshot.
    show             Show current configuration.
    update           Refresh configuration with new changes.
