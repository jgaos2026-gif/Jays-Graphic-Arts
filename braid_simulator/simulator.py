from __future__ import annotations

import runpy
from pathlib import Path

import click


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("example_path", type=click.Path(exists=True, path_type=Path))
def main(example_path: Path) -> None:
    path = example_path
    if path.is_dir():
        path = path / "demo.py"
    if path.suffix != ".py":
        raise click.ClickException("example_path must point to a demo.py file or demo directory")
    runpy.run_path(str(path), run_name="__main__")


if __name__ == "__main__":
    main()
