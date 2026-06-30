#!/usr/bin/env python3
"""Entry point of the A-Maze-ing program.

Loads a configuration file, generates the maze, writes it to the
output file in the required hexadecimal format, and then opens an
interactive terminal menu to regenerate, solve, or recolor the maze.
"""

import time
import sys
from mazegen.parser import load_config, MazeConfig
from mazegen.generator import MazeGenerator


def write_output_file(
    file_path: str, generator: MazeGenerator, cfg: MazeConfig
) -> None:
    """Write the generated maze to the output file in hex format.

    The file contains, in order: one hexadecimal digit per cell
    (one row per line, encoding which of the 4 walls are closed),
    a blank line, the entry coordinates, the exit coordinates, and
    the shortest solution path as a string of N/S/E/W letters.

    Args:
        file_path: Path of the output file to write.
        generator: Generator holding the maze to export.
        cfg: Configuration providing the entry/exit coordinates.
    """

    grid_height = len(generator.maze.grid)
    grid_width = len(generator.maze.grid[0])

    with open(file_path, "w") as f:
        for y in range(grid_height):
            hex_line = ""
            for x in range(grid_width):
                cell = generator.maze.grid[y][x]
                val = 0
                if cell.north:
                    val |= 1
                if cell.east:
                    val |= 2
                if cell.south:
                    val |= 4
                if cell.west:
                    val |= 8

                hex_line += f"{val:X}"
            f.write(hex_line + "\n")

        f.write("\n")
        f.write(f"{cfg.entry.x},{cfg.entry.y}\n")
        f.write(f"{cfg.exit.x},{cfg.exit.y}\n")

        path_str = generator.solve(cfg.entry, cfg.exit)
        f.write(path_str + "\n")


def display_menu() -> None:
    """Prints the user interaction menu to the terminal."""
    print("\n" + "=" * 10 + " A-Maze-ing " + "=" * 10)
    print("1. Re-generate a new maze")
    print("2. Show/Hide path from entry to exit")
    print("3. Rotate maze colors")
    print("4. Quit")


def main() -> None:
    """Main program execution."""

    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt", file=sys.stderr)
        sys.exit(1)

    config_path = sys.argv[1]
    cfg = load_config(config_path)

    gen = MazeGenerator(cfg.width, cfg.height, cfg.seed)

    if (
        gen.maze.is_cell_42(cfg.entry.x, cfg.entry.y)
        or gen.maze.is_cell_42(cfg.exit.x, cfg.exit.y)
    ):
        print(
            "Error: ENTRY or EXIT coordinates fall inside the 42 pattern!",
            file=sys.stderr,
        )
        sys.exit(1)

    gen.generate(
        algorithm=cfg.algorithm,
        start_coord=cfg.entry,
        perfect=cfg.perfect,
    )
    write_output_file(cfg.output_file, gen, cfg)

    show_path = False
    current_color_idx = 0
    colors = [
        "\033[38;5;250m",
        "\033[38;5;211m",
        "\033[38;5;120m",
        "\033[38;5;117m"
        ]

    while True:
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.flush()

        start_coord = cfg.entry
        end_coord = cfg.exit

        p_coords = None
        if show_path:
            raw_path = gen.solve(start_coord, end_coord)
            p_coords = gen.get_path_coords(start_coord, raw_path)

        if gen.maze.error_message:
            print(gen.maze.error_message, file=sys.stderr)
            gen.maze.error_message = None

        gen.maze.print_maze(
            path_coords=p_coords,
            wall_color=colors[current_color_idx],
            entry_coord=cfg.entry,
            exit_coord=cfg.exit
        )

        display_menu()

        try:
            choice = input("Choice? (1-4): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break

        if choice == "1":
            gen = MazeGenerator(cfg.width, cfg.height, None)
            gen.generate(
                algorithm=cfg.algorithm,
                start_coord=cfg.entry,
                perfect=cfg.perfect,
                )
            write_output_file(cfg.output_file, gen, cfg)
            print("\n[!] New maze generated successfully.")

        elif choice == "2":
            if not show_path:
                show_path = True
                raw_path = gen.solve(start_coord, end_coord)
                full_path = gen.get_path_coords(start_coord, raw_path)

                print("[!] Solving maze...")
                sys.stdout.write("\033[?25l")
                sys.stdout.flush()

                for i in range(1, len(full_path) + 1):
                    sys.stdout.write("\033[H\033[J")
                    sys.stdout.flush()

                    partial_path = full_path[:i]
                    gen.maze.print_maze(
                        path_coords=partial_path,
                        wall_color=colors[current_color_idx],
                        entry_coord=start_coord,
                        exit_coord=end_coord
                    )
                    time.sleep(0.04)

                sys.stdout.write("\033[?25h")
                sys.stdout.write("\033[H\033[J")
                sys.stdout.flush()
            else:
                show_path = False
                sys.stdout.write("\033[H\033[J")
                sys.stdout.flush()

        elif choice == "3":
            current_color_idx = (current_color_idx + 1) % len(colors)
            print("\n[!] Wall color rotated.")

        elif choice == "4":
            print("\nGoodbye! :)")
            break
        else:
            print("\n[Invalid choice] Please enter a number between 1 and 4.")


if __name__ == "__main__":
    main()
