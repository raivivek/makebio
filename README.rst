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
    
Philosophy
----------

:code:`makebio` is inspired by project management practices in :code:`@theparkerlab` and "*A Quick
Guide to Organizing Computational Biology Projects*" by WS Noble [#]_. Using
:code:`makebio` is easy and intuitive, and it is flexible enough to be used in a collaborative
environment.

The core idea of :code:`makebio` is to create and manage a specific directory layout for your
project. Using :code:`makebio init`, for example, will setup the following files and directories:

.. code-block::
  project_dir/
      bin/
      control/
      figures/
      notebooks/
      src/
      results/
      data/ --> symlink
      work/ --> symlink
      makebio.toml

This structure allows us to keep:

* analysis files in one place --- :code:`control` directory
* intermediate files in one place --- :code:`work` directory. You may symlink this directory to
  :code:`/tmp`, :code:`/scratch` space, or a destination with a large enough space.
* results (produced from workflows or scripts) in one place --- :code:`results` directory
* raw data in one place --- :code:`data` directory
* essential project files to reproduce your project results

Workflow
^^^^^^^^

#. Setup an empty project directory with :code:`makebio init`.
#. Create a new analysis (:code:`<NAME>`) with :code:`makebio add-analysis`. This will create a (1) new directory in
   the :code:`control/`, and (2) a new directory in the :code:`results/` directory with the name of
   the analysis.
#. Add your analysis files in the :code:`control/<NAME>` directory. Make sure all the output is
   written to the :code:`results/<NAME>` directory.
#. Save your project using :code:`makebio save`.


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

.. rubric:: Footnotes

.. [#] Noble W. S., 2009 A Quick Guide to Organizing Computational Biology
   Projects. PLOS Computational Biology 5: e1000424.
   https://doi.org/10.1371/journal.pcbi.1000424
