import click

from paths_cli.parsing.root_parser import parse
from paths_cli.parameters import OUTPUT_FILE
from paths_cli.errors import MissingIntegrationError
import importlib

def import_module(module_name, format_type=None, install=None):
    try:
        mod = importlib.import_module(module_name)
    except ImportError:
        if format_type is None:
            format_type = module_name

        msg = "Unable to find a parser for f{format_type} on your system."
        if install is not None:
            msg += " Please install f{install} to use this format."

        raise MissingIntegrationError(msg)
    return mod

def load_yaml(f):
    yaml = import_module('yaml', format_type="YAML", install="PyYAML")
    return yaml.load(f.read(), Loader=yaml.FullLoader)

def load_json(f):
    json = import_module('json')  # this should never fail... std lib!
    return json.loads(f.read())

# TODO: It looks like TOML was working with my test dict -- I'll have to see
# if that's an issue with the TOML format or just something weird. I thought
# TOML was equally as flexible (in theory) as JSON.
# def load_toml(f):
#     toml = import_module('toml', format_type="TOML", install="toml")
#     return toml.loads(f.read())


EXTENSIONS = {
    'yaml': load_yaml,
    'yml': load_yaml,
    'json': load_json,
    'jsn': load_json,
    # 'toml': load_toml,
}

def select_loader(filename):
    ext = filename.split('.')[-1]
    try:
        return EXTENSIONS[ext]
    except KeyError:
        raise RuntimeError(f"Unknown file extension: {ext}")

@click.command(
    'compile',
)
@click.argument('input_file')
@OUTPUT_FILE.clicked(required=True)
def compile_(input_file, output_file):
    loader = select_loader(input_file)
    with open(input_file, mode='r') as f:
        dct = loader(f)

    objs = parse(dct)
    # print(objs)
    storage = OUTPUT_FILE.get(output_file)
    storage.save(objs)


CLI = compile_
SECTION = "Debug"
