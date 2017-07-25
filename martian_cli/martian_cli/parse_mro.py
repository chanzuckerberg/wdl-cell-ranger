"""Parses an MRO file into a python representation.

There are two pieces to this. First, pyparsing creates a grammar
for the mro format and uses that to tokenize it into
python objects. Second, those objects are tidied up into something
that's a somewhat intuitive interface.
"""

import collections
import os
import re
import sys

import pyparsing as pp

from martian_cli import utils

def _create_stages(parsed_mro, mro_file_path):
    """Create a list of MartianStages from the output of _parse_mro."""

    stages = []
    for parsed_stage in parsed_mro.stages:
        stage_name = parsed_stage[0]

        def normalize_entry(entry):
            if len(entry) == 3:
                return list(entry) + [None]
            elif len(entry) == 2: # Looking at you, SORT_BY_BC
                return list(entry) + ["default", None]
            else:
                return list(entry)

        normalized_entries = [normalize_entry(e) for e in parsed_stage.stage_entries]
        normalized_splits = [normalize_entry(e) for e in parsed_stage.split]

        stage_inputs = [utils.MartianIOField(*i) for i in normalized_entries if i[0] == 'in']
        stage_outputs = [utils.MartianIOField(*i) for i in normalized_entries if i[0] == 'out']
        stage_splits = [utils.MartianIOField(*i) for i in normalized_splits]
        stage_source = [os.path.join(os.path.dirname(mro_file_path), re.sub(r'^"|"$', "", i[2]))
                        for i in parsed_stage.stage_entries if i[0] == 'src'][0]

        stages.append(utils.MartianStage(
            stage_name,
            stage_inputs,
            stage_outputs,
            stage_splits,
            stage_source))

    return stages

def get_mro_stages(mro_file_path):
    """Walk through a full MRO file structure, following includes, to create their python
    representations.

    Inputs:
        mro_file_path: Path to an MRO file that defines a pipeline

    Returns:
        pipelines
        stages
    """
    stages = {}
    parsed_mro = _parse_mro(mro_file_path)

    if parsed_mro.stages:
        stages_ = _create_stages(parsed_mro, mro_file_path)
        for stage in stages_:
            stages[stage.name] = stage

    return stages


def _parse_mro(mro_file_name):
    """Parse an MRO file into python objects."""

    # A few helpful pyparsing constants
    EQUALS, SEMI, LBRACE, RBRACE, LPAREN, RPAREN = map(pp.Suppress, '=;{}()')
    mro_label = pp.Word(pp.alphanums + '_')
    mro_modifier = pp.oneOf(["in", "out", "src"])
    mro_type = pp.oneOf([
        "bool", "bool[]",
        "int", "int[]",
        "float", "float[]",
        "map", "map[]",
        "string", "string[]", "string[][]",
        "path", "path[]",
        "py"] + \
        utils.MARTIAN_FILETYPES + [x +'[]' for x in utils.MARTIAN_FILETYPES])

    # First parse includes
    include = pp.Literal("@include").suppress() + pp.quotedString
    includes = pp.ZeroOrMore(include).setResultsName("includes")
    includes.addParseAction(pp.removeQuotes)

    # Then parse filetypes
    filetype = pp.Literal("filetype").suppress() + pp.oneOf(utils.MARTIAN_FILETYPES) + SEMI
    filetypes = pp.ZeroOrMore(filetype).setResultsName("filetypes")

    #####################################################
    # Stage
    #####################################################

    # Now define the parts of a stage

    # First we have a "stage entry", which is a line in the stage body, it looks like "in int lane"
    stage_entry = pp.Group(mro_modifier + mro_type + pp.Optional(pp.Word(pp.printables, excludeChars=',')) + pp.Optional(pp.QuotedString('"')))
    # Note that stage entries a comma-delimited, but there's a trailing comma so we need the
    # pp.Empty option for matching
    stage_entries = pp.delimitedList(pp.Or([stage_entry, pp.Empty()]))

    # Each stage can have two parts, the main part and a "split using" part
    split = (pp.Literal("split using").suppress() + LPAREN +
             pp.Optional(pp.Group(stage_entries).setResultsName("split")) + RPAREN)
    stage = pp.Group(pp.Literal("stage").suppress() + mro_label + LPAREN +
                     pp.Group(stage_entries).setResultsName("stage_entries") +
                     RPAREN +
                     pp.Optional(split))

    # Now create a dict of the stages, with the MRO labels for keys
    stages = pp.Dict(pp.ZeroOrMore(stage)).setResultsName("stages")

    #####################################################
    # Pipeline
    #####################################################

    ## Calls
    call_entry = pp.Group(pp.Word(pp.printables, excludeChars="=") + EQUALS +
                          pp.Word(pp.printables, excludeChars=','))
    call_entries = pp.delimitedList(pp.Or([call_entry, pp.Empty()]))
    call_modifier = pp.oneOf(["local", "preflight"])
    call = pp.Group(pp.Literal("call").suppress() + pp.ZeroOrMore(call_modifier).suppress() +
                    mro_label + LPAREN + pp.Group(call_entries).setResultsName("call_entries") +
                    RPAREN)
    calls = pp.Dict(pp.ZeroOrMore(call)).setResultsName("pipeline_calls")

    ## Return
    return_entry = call_entry
    return_entries = pp.delimitedList(pp.Or([return_entry, pp.Empty()]))
    return_ = (pp.Literal("return").suppress() + LPAREN +
               pp.Group(return_entries).setResultsName("pipeline_return") + RPAREN)

    ## Pipeline header
    pipeline_header_entry = pp.Group(mro_modifier + mro_type +
                                     pp.Word(pp.printables, excludeChars=",") +
                                     pp.Optional(pp.quotedString))
    pipeline_header_entries = pp.delimitedList(pp.Or([pipeline_header_entry, pp.Empty()]))

    pipeline = (pp.Literal("pipeline").suppress() + mro_label.setResultsName("pipeline_name") +
                LPAREN + pp.Group(pipeline_header_entries).setResultsName("pipeline_header") +
                RPAREN + LBRACE + calls + return_ + RBRACE)

    mro_file = pp.Each([pp.Optional(includes), filetypes, stages, pp.Optional(pipeline)])
    mro_file.ignore(pp.pythonStyleComment)

    result = mro_file.parseFile(mro_file_name)

    return result
