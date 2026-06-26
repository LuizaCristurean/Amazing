#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   parser.py                                            :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: jmesa-ci <jmesa-ci@student.42malaga.com>     +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/06/11 10:09:18 by czuluaga            #+#    #+#            #
#   Updated: 2026/06/16 13:05:02 by jmesa-ci           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

import sys
from dataclasses import dataclass
from typing import Tuple, Optional

Coord = Tuple[int, int]

mandatory_keys = {'WIDTH', 'HEIGHT', 'ENTRY', 'EXIT', 'OUTPUT_FILE',
                  'PERFECT'}


@dataclass(frozen=True)
class MazeConfig:
    width: int
    height: int
    entry: Coord
    exit: Coord
    output_file: str
    perfect: bool
    seed: Optional[int] = None
    algorithm: str = "backtracker"


def get_coords(coord_str: str, w: int, h: int, key_name: str) -> Coord:
    parts = coord_str.split(',')
    if len(parts) != 2:
        raise ValueError(f"Format {key_name} invalid."
                         "Must be 'x,y'")
    x, y = int(parts[0].strip()), int(parts[1].strip())
    if not (0 <= x < w and 0 <= y < h):
        raise ValueError(f"{key_name} ({x},{y}) out of the maze size")
    return (x, y)


def load_config(file_path: str) -> MazeConfig:
    cfg_data: dict = {}

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
                cfg_data[key.strip().upper()] = val.strip()

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
            raise ValueError("WIDTH and HEIGHT must be positive")

        entry_coord = get_coords(cfg_data['ENTRY'], width, height, 'ENTRY')
        exit_coord = get_coords(cfg_data['EXIT'], width, height, 'EXIT')

        if entry_coord == exit_coord:
            raise ValueError("ENTRY and EXIT can't be identical.")

        perfect_str = cfg_data['PERFECT'].lower()
        if perfect_str in ('true', 'True'):
            perfect = True
        elif perfect_str in ('false', 'False'):
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
