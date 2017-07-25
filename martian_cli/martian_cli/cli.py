"""Module to define and expose the CLI to Martina

Contains the entry point for the package.
"""

import argparse
import json
import os
import re
import sys
import traceback

from martian_cli import adapters, mro, utils

def verify_environment():
    """Check that required environment values are present.

    This is just checking for MROPATH and the ability to import
    martian.
    """

    if "MROPATH" not in os.environ:
        raise EnvironmentError(
            "MROPATH is not in the environment. You probably need to source "
            "sourceme.bash in cellranger before running this tool")

    try:
        import martian
    except ImportError:
        print sys.path
        traceback.print_exc()
        raise ImportError(
            "Could not import martian. You probably need to source "
            "sourceme.bash in cellranger before running this tool.")

def stage_list(args):
    """Function that handles `martian stage list`"""

    for stage in args.stages:
        print stage

def stage_describe(args):
    """Function that handles `martian stage describe <stage_name>`"""

    stage = args.stages[args.stage_name]

    print "Stage:", stage.name, "\n"
    print "Inputs:"
    for input_ in stage.inputs:
        print "\t", input_.name, input_.type, input_.help or ""

    print "\n"
    print "Outputs:"
    for output in stage.outputs:
        print "\t", output.name, output.type, output.help or ""

    print "\n"
    print "Splits:"
    for split in stage.splits:
        print "\t", split.name, split.type, split.help or ""

    print "\n"
    print "Source directory:"
    print "\t", stage.source

def stage_run(args):
    """Function that handles `martian stage run <stage> <phase> ...`"""
    print "stage_run args:", args
    if args.phase == "split":
        output = adapters.split(args.stage, args)
    if args.phase == "main":
        output = adapters.main(args.stage, args)
    if args.phase == "join":
        ouptut = adapters.main(args.stage, args)



def get_parser(stages):
    """Create the argument parser for the CLI."""

    # martian
    parser = argparse.ArgumentParser(prog="martian")
    subparsers = parser.add_subparsers()

    # martian stage
    stage_parser = subparsers.add_parser(
        "stage", help="Work with Martian stages.")

    stage_subparsers = stage_parser.add_subparsers(
        title="Stage subcommands",
        help="Actions than can be performed on Martian stages.")

    # martian stage list
    stage_list_parser = stage_subparsers.add_parser(
        "list",
        help="List all available stages.")
    stage_list_parser.set_defaults(func=stage_list)
    stage_list_parser.set_defaults(stages=stages)

    # martian stage describe <stage_name>
    stage_describe_parser = stage_subparsers.add_parser(
        "describe",
        help="Describe the inputs, outputs, and source location of a stage")
    stage_describe_parser.add_argument(
        "stage_name",
        help="Name of the stage to describe")
    stage_describe_parser.set_defaults(func=stage_describe)
    stage_describe_parser.set_defaults(stages=stages)

    # martian stage run <stage_name> <stage_phase> <stage_args...>
    stage_run_parser = stage_subparsers.add_parser(
        "run",
        help="Run a stage")

    stage_run_subparsers = stage_run_parser.add_subparsers(
        title="Stages available to be run",
        help="Names of available stages.")

    for stage in stages.values():

        individual_stage_parser = stage_run_subparsers.add_parser(
            stage.name,
            help="Execute stage " + stage.name)
        individual_stage_subparsers = individual_stage_parser.add_subparsers()

        available_stage_phases = ['split', 'join', 'main'] if stage.splits else ['main']

        for phase in available_stage_phases:
            phase_parser = individual_stage_subparsers.add_parser(
                phase,
                help='Run the ' + phase + ' of ' + stage.name)


            phase_parser.set_defaults(func=stage_run)
            phase_parser.set_defaults(phase=phase)
            phase_parser.set_defaults(stage=stage)

            for input_ in utils.list_stage_inputs(stage, phase):
                help_message = "Type: " + input_.type
                if input_.help:
                    help_message += " Help: " + input_.help

                phase_parser.add_argument(
                    "--" + input_.name,
                    type=martian_type_to_python_type(input_.type),
                    nargs=martian_type_to_nargs(input_.type),
                    default=None,
                    help=help_message)

    return parser

def strip_quotes(file_arg):
    """Strip leading and trailing quotes.

    These are showing up in paths...
    """
    return re.sub("^[\'\"]|[\'\"]$", "", file_arg)

def martian_type_to_python_type(martian_type):

    MARTIAN_TO_PYTHON = {"path": strip_quotes,
                         "int": int,
                         "bool": utils.str_to_bool,
                         "float": float,
                         "string": str,
                         "File": strip_quotes,
                         "map": json.loads}
    for ftype in utils.MARTIAN_FILETYPES:
        MARTIAN_TO_PYTHON[ftype] = str

    return MARTIAN_TO_PYTHON[martian_type.strip('[]')]

def martian_type_to_nargs(martian_type):

    if martian_type.endswith("[]"):
        return "*"
    else:
        return '?'


def main():

    # Make sure we're running in the cellranger environment
    verify_environment()

    # Load all the available stages
    stages = mro.load_stages()

    # Create an argument parser out of the stages
    parser = get_parser(stages)

    args = parser.parse_args()
    args.func(args)
