#!/usr/bin/env python3
"""Configuration file parsing and validation for the maze generator.

This module reads a simple ``KEY=VALUE`` configuration file, validates
every mandatory and optional setting, and returns a ``MazeConfig``
ready to be used by the rest of the program. Any invalid or missing
configuration causes a clear error message and a clean exit, instead
of letting the program crash with a raw traceback.
"""

import sys
from dataclasses import dataclass
from typing import Dict, Optional
from .write_maze import Coord


mandatory_keys = {'WIDTH', 'HEIGHT', 'ENTRY', 'EXIT', 'OUTPUT_FILE',
                  'PERFECT'}


@dataclass(frozen=True)
class MazeConfig:
    """Validated settings loaded from the configuration file."""

    width: int
    height: int
    entry: Coord
    exit: Coord
    output_file: str
    perfect: bool
    seed: Optional[int] = None
    algorithm: str = "backtracker"


def get_coords(coord_str: str, w: int, h: int, key_name: str) -> Coord:
    """Parse and validate a "x,y" coordinate string.

    Args:
        coord_str: Raw value from the config file, expected as "x,y".
        w: Maze width, used to validate the x bound.
        h: Maze height, used to validate the y bound.
        key_name: Name of the config key (used in error messages).

    Returns:
        The parsed coordinate as a ``Coord``.

    Raises:
        ValueError: If the format is invalid or the coordinate falls
            outside the maze bounds.
    """

    parts = coord_str.split(',')
    if len(parts) != 2:
        raise ValueError(f"Format {key_name} invalid."
                         "Must be 'x,y'")
    x, y = int(parts[0].strip()), int(parts[1].strip())
    if not (0 <= x < w and 0 <= y < h):
        raise ValueError(f"{key_name} ({x},{y}) out of the maze size")
    return Coord(x, y)


def load_config(file_path: str) -> MazeConfig:
    """Load, validate and return the maze configuration from a file.

    Reads ``KEY=VALUE`` lines (ignoring blank lines and ``#``
    comments), checks every mandatory key is present, and validates
    each value's type and range. On any error - missing file, bad
    syntax, missing key, or invalid value - prints a clear message to
    stderr and exits the program with status 1, instead of raising an
    unhandled exception.

    Args:
        file_path: Path to the configuration file.

    Returns:
        A fully validated ``MazeConfig``.
    """

    cfg_data: Dict[str, str] = {}
    allowed_keys = mandatory_keys | {'SEED', 'ALGORITHM'}

    try:
        with open(file_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                extracted_line = line.split('#', 1)[0].strip()
                if not extracted_line:
                    continue

                if '=' not in extracted_line:
                    raise ValueError(f"Line {line_num}: Format invalid. "
                                     "Missing '='")

                key, val = extracted_line.split('=', 1)
                clean_key = key.strip().upper()

                if clean_key not in allowed_keys:
                    continue

                cfg_data[clean_key] = val.strip()

    except FileNotFoundError:
        print(f"Error: Configuration file '{file_path}' not found.",
              file=sys.stderr)
        sys.exit(1)
    except Exception as error:
        print(f"Error reading the file: {error}", file=sys.stderr)
        sys.exit(1)

    missing = mandatory_keys - cfg_data.keys()
    if missing:
        print(f"Error: Mandatory keys are missing: {', '.join(missing)}",
              file=sys.stderr)
        sys.exit(1)

    try:
        width = int(cfg_data['WIDTH'])
        height = int(cfg_data['HEIGHT'])
        if width <= 0 or height <= 0:
            raise ValueError("WIDTH and HEIGHT must be bigger than 0")

        entry_coord = get_coords(cfg_data['ENTRY'], width, height, 'ENTRY')
        exit_coord = get_coords(cfg_data['EXIT'], width, height, 'EXIT')

        if entry_coord == exit_coord:
            raise ValueError("ENTRY and EXIT can't be identical.")

        perfect_str = cfg_data['PERFECT'].lower()
        if perfect_str == 'true':
            perfect = True
        elif perfect_str == 'false':
            perfect = False
        else:
            raise ValueError("PERFECT must be a boolean value.")

        output_file = cfg_data['OUTPUT_FILE']
        if not output_file:
            raise ValueError("OUTPUT_FILE can't be empty.")

        if 'SEED' in cfg_data:
            seed = int(cfg_data['SEED'])
        else:
            seed = None

        algorithm = cfg_data.get('ALGORITHM', "backtracker")

        return MazeConfig(
            width=width,
            height=height,
            entry=entry_coord,
            exit=exit_coord,
            output_file=output_file,
            perfect=perfect,
            seed=seed,
            algorithm=algorithm
        )

    except ValueError as error1:
        print(f"Validation error on the cofiguration values: {error1}",
              file=sys.stderr)
        sys.exit(1)
