import argparse
import json
import os
import sys

import martian
from martian_cli import utils

# Close enough!
MartianIOObject = argparse.Namespace

def _construct_outs(martian_io_fields):
    """Build an outs object that fills expected output file names."""
    outs = {}
    for field in martian_io_fields:
        if field.type in utils.MARTIAN_FILETYPES:
            outs[field.name] = field.name + '.' + field.type
        else:
            outs[field.name] = None
    return MartianIOObject(**outs)

def _write_outs(outs, martian_io_fields):
    for field in martian_io_fields:
        if field.type not in utils.MARTIAN_FILETYPES:
            with open(field.name, 'w') as outf:
                json.dump(getattr(outs, field.name), outf)

def _common(stage):
    """This is very bad."""
    # oh my god
    import __builtin__
    __builtin__.metadata = martian.Metadata(stage.source, "files", "run", "main")
    sys.path.append(os.path.dirname(stage.source))
    __builtin__.module = __import__(os.path.basename(stage.source))

def split(stage, cli_args):
    """Run a split phase of a stage."""

    _common(stage)

    args = MartianIOObject(
        **{k.name: getattr(cli_args, k.name) for k in stage.inputs})

    stage_defs = None
    # Now continue with the theme of screwing with the environment, and exec the module
    env = globals()
    env.update(locals())
    exec("stage_defs = module.split(args)", env, env)

    return stage_defs["chunks"]

def main(stage, cli_args):
    """Run a main phase of a stage."""

    _common(stage)

    # Build the args. The args of a main stage are all the "inputs" plus everything
    # in "split using"
    args = MartianIOObject(
        **{k.name: getattr(cli_args, k.name) for k in stage.inputs + stage.splits})

    # Build the outs object, which is just the stage output fields
    outs = _construct_outs(stage.outputs)

    # Now continue with the theme of screwing with the environment, and exec the module
    env = globals()
    env.update(locals())
    exec("module.main(args, outs)", env, env)
    print "outs", outs
    _write_outs(outs, stage.outputs)

    return outs

def join(stage, cli_args):
    """Run a join phase of a stage."""

    _common(stage)

    # The inputs to a join stage are complicated. There are four inputs
    # 1. args - these are the same as the args to split, which is just stage inputs
    # 2. outs - this is the stage outputs, constructed in the usual way
    # 3. chunk_defs - a list of the inputs provided to each of the main steps. So these
    #        are fields from splits
    # 4. chunk_outs - a list of the outputs from each of the main steps. So these are
    #        fields from outs

    # Also, the inputs to join have a little tag in the beginning, "in.", "split.",
    # and "out.".

    args = MartianIOObject(
        **{k.name: getattr(cli_args, "in." + k.name) for k in stage.inputs})
    outs = _construct_outs(stage.outputs)
    chunk_defs = utils.MartianIOField(
        **{k.name: getattr(cli_args, "split." + k.name) for k in stage.splits})
    chunk_outs = utils.MartianIOField(
        **{k.name: getattr(cli_args, "out." + k.name) for k in stage.outputs})


    # Now continue with the theme of screwing with the environment, and exec the module
    env = globals()
    env.update(locals())
    exec("module.join(args, outs, chunk_defs, chunk_outs)", env, env)

    return outs
