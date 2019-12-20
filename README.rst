## Project

Helper utility to quickly setup my analysis.

#### Question

Whether to use this or use cookiecutter? What I'll be doing here is basically
a subset of what cookiecutter does -- perhaps I can just wrap cookiecutter's API
to do the desired actions.

Use '.project.yaml' for configuration? -- what configuration?

project init -- setups a directory structure
project save -- commits all the control/source files
project add-analysis -- setups a analysis directory (control and the work-dir output)
project add-data -- setups a data directory [optionally, should mark it read-only, and hash the files to a checksum?]

[RFC] project add-analysis --snakemake -- adds a quick snakemake analysis files
[RFC] project add-analysis --nextflow




## User story

I go into my root directory; and run:
    `project init xxx --linkto yyy`

- This will setup analysis directory where work/ links to the target
- It should also prompt for some metadata information


How will it do it; if a directory already exists with that name, then give error.