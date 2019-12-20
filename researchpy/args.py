import argparse
import textwrap

__description__ = """
Description
-----------
project -- for the lack of better name.

* `analysis` and `data` directories are prefixed with the date of creation.
   For example, 2019-04-20_createTracks or 2019-05-01_fastq.

* `freeze` marks the target directory and all files within to be read-only.
   By default, it marks everything under `data/` to be read-only.

See additional options by typing -h/--help for each subcommand.
"""

epilog = """
Comments
--------
    GitHub: github.com/raivivek/project
    Twitter: @raivivek_
"""

parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=__description__,
    epilog=epilog,
)
subparsers = parser.add_subparsers()

# Setup
init_parse = subparsers.add_parser("init")
init_parse.add_argument("path", help="Project root directory")
init_parse.add_argument(
    "--linkto", help="Work directory (scratch, for example)", required=True
)

# Save
save_parse = subparsers.add_parser("save")
save_parse.add_argument("path", help="Project directory")

# Commands for adding analysis
add_analysis_parse = subparsers.add_parser("add-analysis")
add_analysis_parse.add_argument("analysis", help="Analysis name")
add_analysis_parse.add_argument(
    "--snakemake", action="store_true", help="Add Snakemake analysis"
)
add_analysis_parse.add_argument(
    "--nextflow", action="store_true", help="Add Nextflow analysis"
)

# Commands for adding data
add_data_parse = subparsers.add_parser("add-data")
add_data_parse.add_argument("name", help="Name (is prefixed with date)")

# Commands for "freezing" analysis
freeze_parse = subparsers.add_parser("freeze")


def parse_args():
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    parse_args()
