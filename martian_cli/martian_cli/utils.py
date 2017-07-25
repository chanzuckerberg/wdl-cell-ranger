import argparse
import collections

MARTIAN_FILETYPES = ["bam", "bam.bai", "bed", "cloupe", "csv", "fasta",
                     "fasta.fai", "fastq", "gtf", "h5", "html", "json",
                     "pickle", "sam", "script", "tsv", "vloupe"]

MartianIOField = collections.namedtuple(
    "MartianIOField",
    ["modifier",    # A string in ["in", "out"]
     "type",        # A string like "json", "int", "float", "map[]", etc.
     "name",        # A string that identifies the field
     "help"])       # An optional help message string

MartianStage = collections.namedtuple(
    "MartianStage",
    ["name",        # A string that identifies the stage
     "inputs",      # A list of MartianIOFields
     "outputs",     # A list of MartianIOFields
     "splits",      # A list of MartianIOFields
     "source"])     # A string that is a path to a directory that contains an __init__.py

MartianCall = collections.namedtuple(
    "MartianCall",
    ["name",        # A string identifying callable that is being called
     "assignments"])# A dict with keys for input fields of the callable and values for the
                    #   assigned value. Note that the value needs some parsing, so "self.lanes"
                    #   refers to the "lanes" input to the pipeline, etc.

MartianPipeline = collections.namedtuple(
    "MartianPipeline",
    ["name",        # A string identifying the pipeline
     "inputs",      # A list of MartianIOFields
     "outputs",     # A list of MartianIOFields
     "calls",       # A list of MartianCalls
     "return_"])    # A dict with keys for the pipeline's output names and values for the
                    #   assignment of call outputs to pipeline outputs


# Functions to translate a MartianStage into the expected interface for each of the
# phases: split, main, and join

def list_stage_inputs(stage, phase):
    if phase == 'split':
        return stage.inputs
    elif phase == 'main':
        return stage.inputs + stage.splits
    elif phase == 'join':
        inputs = []
        for i in stage.inputs:
            inputs.append(MartianIOField(i.modifier, i.type, 'in.' + i.name, i.help))
        for i in stage.splits:
            inputs.append(MartianIOField(i.modifier, i.type, 'split.' + i.name, i.help))
        for i in stage.outputs:
            inputs.append(MartianIOField(i.modifier, i.type, 'out.' + i.name, i.help))

        return inputs

def str_to_bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')
