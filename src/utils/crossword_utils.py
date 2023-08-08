import os
import puz
import math

"""
Manually assigned clue types to clues in the crossword puzzles by @meghabyte.
We follow the reasoning categorization in https://arxiv.org/pdf/2205.09665.pdf.
- Knowledge:  Clues that require knowledge of his- tory, scientific terminology, pop culture, or other trivia topics, often proper nouns
    - e.g. "Astronaut Jemison", (mae)
- Definition:  rough definitions or synonyms of the answer
    - e.g. "Sensible", (sane)
- Commonsense: Relational reasoning of well-known entitites
    e.g. "Ocho minus cinco", (tres)
- Wordplay: Clues that involve reasoning about metalinguistic patterns (e.g. puns or heteronyms).
    e.g. "Flight path?", (aisle)
- Phrase: Involve common phrases or multi-word expressions.
    e.g. "Well, obviously!", (noduh)
- Cross-Reference: Requires knowledge of other puzzle elements or theme
    e.g. See 45-Across (baba)
"""

puzzle_61 = {
    "across": {
        1: "knowledge",
        20: "knowledge",
        39: "cross-ref",
        60: "cross-ref",
        62: "cross-ref",
        47: "sense",
        15: "sense",
        9: "definition",
        43: "definition"

    },
    "down": {
        9: "cross-ref",
        42: "wordplay",
        48: "wordplay",
        4: "phrase",
        28: "phrase",
        43: "definition",
        33: "definition",
        62: "wordplay",
        61: "sense",
        6: "sense"

    }
}


puzzle_151 = {
    "across": {
        1: "knowledge",
        26: "definition",
        29: "sense",
        65: "phrase",
        20: "wordplay",
        36: "phrase",
        25: "phrase",
        42: "sense",
        61: "sense"

    },
    "down": {
        54: "knowledge",
        8: "definition",
        58: "sense",
        13: "phrase",
        50: "wordplay",

    }
}

puzzle_173 = {
    "across": {
        1: "knowledge",
        17: "sense",
        63: "cross-ref",
        68: "knowledge",
        18: "definition",
        71: "wordplay",
        66: "phrase",
        30: "phrase"
    },
    "down": {
        49: "phrase",
        35: "phrase",
        47: "wordplay",
        7: "wordplay",
        5: "definition",
        26: "sense",
        57: "wordplay"
    }
}

puzzle_187 = {
    "across": {
        45: "cross-ref",
        33: "wordplay",
        64: "wordplay",
        23: "sense",
        54: "definition",
        53: "knowledge"


    },
    "down": {
        26: "cross-ref",
        29: "phrase",
        42: "phrase",
        57: "sense",
        51: "definition",
        4: "knowledge"
    }
}

puzzle_191 = {
    "across": {
        59: "wordplay",
        53: "knowledge",
        52: "knowledge",
        18: "cross-ref",
        68: "sense"


    },
    "down": {
        12: "wordplay",
        36: "definition",
        41: "definition",
        62: "sense",
        4: "phrase",
        35: "phrase",
        10: "knowledge",
        12: "knowledge"
    }
}

CLUE_TYPES_DICT = {
    61: puzzle_61,
    151: puzzle_151,
    173: puzzle_173,
    187: puzzle_187,
    191: puzzle_191
}

CLUE_TYPES_CATEGORIES = ["wordplay", "definition",
                         "sense", "phrase", "knowledge", "cross-ref"]


class Puzzle:
    def __init__(self, gid, path_dir):
        self.gid = gid
        self.puzzle = puz.read(os.path.join(path_dir, str(gid)+".puz"))
        self.clues = {"across": {}, "down": {}}
        self.process_clues()

    def get_grid_cell(self, cell_num):
        numbering = self.puzzle.clue_numbering()
        row = math.floor(cell_num / numbering.width)
        col = cell_num % numbering.width
        return [row, col]

    def process_clues(self):
        numbering = self.puzzle.clue_numbering()
        for across_clue in numbering.across:
            cells = [across_clue["cell"]+i for i in range(across_clue["len"])]
            solution = "".join([self.puzzle.solution[c] for c in cells])
            grid_cells = [self.get_grid_cell(c) for c in cells]
            clue_dict = {"question": across_clue["clue"],
                         "solution": solution,
                         "cells": grid_cells}
            self.clues["across"][across_clue["num"]] = clue_dict
        for down_clue in numbering.down:
            cells = [down_clue["cell"]+(i*numbering.width) for i in range(down_clue["len"])]
            solution = "".join([self.puzzle.solution[c] for c in cells])
            grid_cells = [self.get_grid_cell(c) for c in cells]
            clue_dict = {"question": down_clue["clue"],
                         "solution": solution,
                         "cells": grid_cells}
            self.clues["down"][down_clue["num"]] = clue_dict

    def get_cells_for_clue(self, number, direction):
        """Returns all grid cells corresponding to a given crossword clue"""
        return self.clues[direction][number]["cells"]

    def get_solution_for_clue(self, number, direction):
        """Returns text solution to a given crossword clue"""
        return self.clues[direction][number]["solution"]

    def get_all_clues(self):
        """Returns list of all clues in the puzzle"""
        all_clues = []
        for clue_num in self.clues["across"].keys():
            all_clues.append(("across", clue_num))
        for clue_num in self.clues["down"].keys():
            all_clues.append(("down", clue_num))
        return all_clues

    def get_all_clue_questions(self):
        return [c["question"].lower() for c in self.clues["across"].values()]+[c["question"].lower() for c in self.clues["down"].values()]

    def get_question_for_clue(self, number, direction):
        """Returns question for a given crossword clue"""
        return self.clues[direction][number]["question"]

    def get_clue_for_cell(self, row, col):
        """Returns the clue that corresponds to a cell -- defaults to across clue if ambiguous"""
        for clue_num in self.clues["across"].keys():
            if([row, col] in self.clues["across"]["cells"]):
                return (clue_num, "across")
        for clue_num in self.clues["down"].keys():
            if([row, col] in self.clues["down"]["cells"]):
                return (clue_num, "down")
        return None

    def get_user_solution_for_clue(self, number, direction, user_grid):
        """Returns user's text solution to a given crossword clue"""
        cells = self.get_cells_for_clue(number, direction)
        user_solution = ""
        for row, col in cells:
            if(len(user_grid[row][col]) == 0):
                user_solution += " "
            else:
                user_solution += user_grid[row][col]
        return user_solution

    def grade_clue(self, number, direction, user_grid):
        clue_score = 0
        cells = self.get_cells_for_clue(number, direction)
        user_solution = ""
        for row, col in cells:
            if(len(user_grid[row][col]) == 0):
                user_solution += " "
            else:
                user_solution += user_grid[row][col]
        crossword_solution = self.get_solution_for_clue(number, direction).lower()
        for letter_index in range(len(crossword_solution)):
            if(crossword_solution[letter_index] == user_solution[letter_index].lower()):
                clue_score += 1
        clue_len = len(crossword_solution)
        return clue_score, clue_len

    def grade_puzzle_letter(self, user_grid):
        score = 0
        total = 0
        for clue in self.get_all_clues():
            clue_score, clue_len = self.grade_clue(number=clue[1], direction=clue[0], user_grid=user_grid)
            score += clue_score
            total += clue_len
        return score/total

    def grade_puzzle_clue(self, user_grid):
        score = 0
        total = 0
        for clue in self.get_all_clues():
            clue_score, clue_len = self.grade_clue(number=clue[1], direction=clue[0], user_grid=user_grid)
            score += (clue_score == clue_len)
            total += 1
        return score/total

    def get_clue_type(self, number, direction):
        if(number in CLUE_TYPES_DICT[self.gid][direction].keys()):
            clue_type = CLUE_TYPES_DICT[self.gid][direction][number]
            return clue_type.strip().lower()
        else:
            return None

    def get_all_clues_by_type(self, clue_type):
        clues = []
        for direction in self.clues.keys():
            for number in self.clues[direction].keys():
                if(self.get_clue_type(number=number, direction=direction) == clue_type):
                    clues.append((direction, number))
        return clues

    def grade_type_clues(self, clue_type, user_grid):
        clue_set = self.get_all_clues_by_type(clue_type)
        score = 0
        total = 0
        for clue in clue_set:
            clue_score, clue_len = self.grade_clue(number=clue[1], direction=clue[0], user_grid=user_grid)
            score += (clue_score == clue_len)
            total += 1
        if(total == 0):
            return -1
        else:
            return score/total
