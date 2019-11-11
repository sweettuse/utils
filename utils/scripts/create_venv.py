import click
from pathlib import Path
import subprocess

__author__ = 'acushner'


@click.command()
@click.option('-v', '--version', default='3.7', help='e.g., 3.7')
@click.option('-n', '--name-override', default=None)
@click.argument('directory', nargs=1, required=True)
def run(directory: str, version: str, name_override: str):
    """"""
    if not directory.startswith(('~', '/')):
        raise ValueError('must path either full or ~ path')

    directory = Path(directory).expanduser()
    name = name_override or directory.name
    print(directory, version, name)
    venv = directory / f'.{name}'
    alias = directory / '.venv'
    v_cmd = f'python{version} -m venv {venv}'
    ln_cmd = f'ln -s {venv} {alias}'
    print(v_cmd)
    print(ln_cmd)

    out = '\n'.join(('#!/bin/bash',
                     f'export PYTHONPATH=$ORIG_PYTHON_PATH:{directory}',
                     f'. {venv}/bin/activate\n'))
    _exec(v_cmd, ln_cmd, out, name)


def _exec(v_cmd, ln_cmd, out, name):
    subprocess.run(v_cmd, shell=True)
    subprocess.run(ln_cmd, shell=True)
    with open(Path('~/scripts').expanduser() / f've_{name}', 'w') as f:
        f.write(out)


def __main():
    return run()


if __name__ == '__main__':
    __main()
