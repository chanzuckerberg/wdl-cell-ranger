import os

from martian_cli import parse_mro

__all__ = ["load_stages"]

def load_stages_from_dir(mro_dir):
    stages = {}
    for file_name in os.listdir(mro_dir):
        if file_name.endswith(".mro"):
            stages.update(parse_mro.get_mro_stages(os.path.join(mro_dir, file_name)))
    return stages

def load_stages():
    stages = {}
    for mro_dir in os.environ["MROPATH"].split(':'):
        stages.update(load_stages_from_dir(mro_dir))
    return stages
