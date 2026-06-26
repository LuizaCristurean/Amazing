#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   write_maze.py                                        :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: lcristur <lcristur@student.42malaga.com>     +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/06/19 14:06:29 by jmesa-ci            #+#    #+#            #
#   Updated: 2026/06/26 12:51:33 by lcristur           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

import sys
from typing import NamedTuple


class Coord(NamedTuple):
    x: int
    y: int


class Cell:
    def __init__(self):
        self.north = True
        self.south = True
        self.east = True
        self.west = True
        self.visited = False
        self.is_42 = False


class Maze:
    def __init__(self, width: int, height: int):
        self.m_width: int = width
        self.m_height: int = height
        self.grid = [[Cell() for _ in range(width)] for _ in range(height)]

        # Intentamos aplicar el patrón del "42" en el centro
        self._apply_42_pattern()

    def _apply_42_pattern(self):
        p42 = [
            [1, 0, 0, 0, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 0, 1, 1, 1],
            [0, 0, 1, 0, 1, 0, 0],
            [0, 0, 1, 0, 1, 1, 1]
        ]
        p42_h = 5
        p42_w = 7

        # Center the pattern
        start_y = (self.m_height - p42_h) // 2
        start_x = (self.m_width - p42_w) // 2

        # Check if the pattern fits in our maze
        if (start_y < 1 or start_x < 1 or
                (self.m_height - start_y - p42_h) < 1 or
                (self.m_width - start_x - p42_w) < 1):
            print("Error: The size of the Maze is not big enough to "
                  "fit the 42 logo pattern", file=sys.stderr)
            return

        for y in range(p42_h):
            for x in range(p42_w):
                if p42[y][x] == 1:
                    self.grid[start_y + y][start_x + x].is_42 = True

    def print_maze(self):
        # ANSI COLORS
        GREEN_BG = "\033[42m"
        RESET = "\033[0m"

        # Top boundary line
        top_line = ""
        for x in range(self.m_width):
            top_line += "█" + ("███" if self.grid[0][x].north else "   ")
        print(top_line + "█")

        for y in range(self.m_height):
            mid_line = ""   # EAST/WEST Walls
            bot_line = ""   # SOUTH and corners

            for x in range(self.m_width):
                cell = self.grid[y][x]

                if cell.west:
                    mid_line += "█"
                else:
                    # PAINT 42 CELLS BACKGROUND
                    if cell.is_42 or (x > 0 and self.grid[y][x - 1].is_42):
                        mid_line += f"{GREEN_BG} {RESET}"
                    else:
                        mid_line += " "

                if cell.is_42:
                    mid_line += f"{GREEN_BG}   {RESET}"
                else:
                    mid_line += "   "

                if cell.south:
                    bot_line += "████"
                else:
                    if cell.is_42 or (y < self.m_height - 1
                                      and self.grid[y + 1][x].is_42):
                        bot_line += f"█{GREEN_BG}   {RESET}"
                    else:
                        bot_line += "█   "

            if self.grid[y][-1].east:
                mid_line += "█"
            else:
                if self.grid[y][-1].is_42:
                    mid_line += f"{GREEN_BG} {RESET}"
                else:
                    mid_line += " "

            # Bottom right corner
            bot_line += "█"

            # Print current line
            print(mid_line)
            print(bot_line)

    def open_walls(self, coord: Coord, direction: str):
        opposite = {
            "north": "south",
            "south": "north",
            "east": "west",
            "west": "east"
        }

        move = {
            "north": (-1, 0),
            "south": (1, 0),
            "east":  (0, 1),
            "west":  (0, -1)
        }

        if direction not in opposite:
            return
        dy, dx = move[direction]
        ny, nx = coord.y + dy, coord.x + dx

        if not (0 <= ny < self.m_height and 0 <= nx < self.m_width):
            return

        current_cell = self.grid[coord.y][coord.x]
        neighbor_cell = self.grid[ny][nx]

        # Breaks actuall Cell wall
        setattr(current_cell, direction, False)
        # Breaks neighbour opposite Cell wall
        setattr(neighbor_cell, opposite[direction], False)


maze = Maze(11, 11)
maze.print_maze()
