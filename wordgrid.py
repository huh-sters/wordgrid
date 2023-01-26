#!/usr/bin/env python3
import sys
import os
import io
from string import ascii_uppercase
from random import choice, randint
from typing import Tuple, List
from zipfile import ZipFile
# from datetime import datetime
# import math
"""
Word grid game
"""

class Settings:
    grid_width: int = 10
    grid_height: int = 10
    dictionary: List[str]
    filler: str = "."
    _color: bool = None

    @classmethod
    def has_color(cls) -> bool:
        """
        Check for terminal colors, we have to be at least in a TTY and any of:
        * Not windows
        * ANSICON or WT_SESSION present
        * VS Code terminal
        * Colorama installed
        """
        if cls._color:
            return cls._color

        cls._color = False

        if hasattr(sys.stdout, "isatty") and sys.stdout.isatty():
            if sys.platform != "win32":
                cls._color = True

            if "ANSICON" in os.environ or "WT_SESSION" in os.environ:
                cls._color = True

            if os.getenv("TERM_PROGRAM") == "vscode":
                cls._color = True

            try:
                import colorama
                cls._color = True
            except (ImportError, OSError):
                pass

        return cls._color

    @classmethod
    def load_dictionary(cls) -> None:
        mod_path = os.path.dirname(os.path.abspath(__file__))
        with ZipFile(os.path.join(mod_path, "english_dic.zip")) as dic_zip:
            with io.TextIOWrapper(dic_zip.open("english_dic.txt"), encoding="utf-8") as dic_handle:
                cls.dictionary = dic_handle.read().splitlines()

def print_color(text: str, color: str, end="\n") -> str:
    if not Settings.has_color():
        print(text, end=end)
        return

    ansi_colors = {
        "blue": "\033[94m",
        "cyan": "\033[96m",
        "green": "\033[92m",
        "white": "\033[90m",
        "red": "\033[91m"
    }

    start_ansi = ansi_colors.get(color, '\033[90m')
    end_ansi = "\033[0m"
    print(f"{start_ansi}{text}{end_ansi}", end=end)

class InvalidWord(Exception):
    pass


def calculate_seed() -> Tuple[str, Tuple[int, int]]:
    """
    Using the current date, calculate the letter and coordinates
    """
    # TODO: Figure this part out
    # year, month, day, _, _, _, _ = datetime.today()

    # weekday = datetime.today().weekday()
    # quarter = (datetime.today().month - 1) // 3
    # def rotate_right(value: str, count: int) -> str:
    #     return value[-(count % 26):] + value[:-(count % 26)]

    # Rotate the upper case characters by X value
    # day = int(datetime.today().strftime("%j"))
    # letter_index = int(datetime.today().strftime("%V")) // 2  # Index choice
    # alphabet = rotate_right(ascii_uppercase, int(math.pow(day, letter_index)))
    # Number from 1-26 (5 bits)
    # Grid location from 0-9 for x and y
    # 1
    # 68421
    # -----
    # 11010

    return (choice(ascii_uppercase), (randint(0, Settings.grid_width - 1), randint(0, Settings.grid_height - 1)))




def validate(seed: Tuple[str, Tuple[int, int]], wordlist: List[Tuple[str, str]]) -> bool:
    """
    Validate the wordlist:
    * Word starts with the last letter of the previous word
    * Words fit in grid
    * No repeat words
    * Letters do not clash with letters already in the grid
    * Word not in the dictionary
    """
    # Check first letter
    last_letter = seed[0]  # Seed letter
    x, y = seed[1]
    for word in wordlist:
        if word[0] not in Settings.dictionary:
            raise InvalidWord(f"{word[0]} is not in the dictionary")
        if word[0][0] != last_letter:
            raise InvalidWord(f"{word[0]} does not start with {last_letter}")
        last_letter = word[0][-1]
        if word[1] == "N":
            y -= len(word[0]) - 1
        elif word[1] == "S":
            y += len(word[0]) - 1
        elif word[1] == "E":
            x += len(word[0]) - 1
        elif word[1] == "W":
            x -= len(word[0]) - 1
        if not 0 <= x <= Settings.grid_width - 1:
            raise InvalidWord(f"{word[0]} falls outside of the x grid")
        if not 0 <= y <= Settings.grid_height - 1:
            raise InvalidWord(f"{word[0]} falls outside of the y grid")

    # No repeat words
    repeatwordlist = [word[0] for word in wordlist]
    if len(wordlist) != len(set(repeatwordlist)):
        raise InvalidWord(f"Word already used")

    # Check for clashing letters
    # Initialise the grid
    grid = [ [Settings.filler] * Settings.grid_width for _ in range(Settings.grid_height)]

    # Set the seed in case there are no words in the list
    grid[seed[1][1]][seed[1][0]] = seed[0]

    # Place each word in the grid starting with the seed location
    x, y = seed[1]
    for word in wordlist:
        for index, letter in enumerate(word[0]):
            if index > 0 and grid[y][x] not in [Settings.filler, letter]:  # Clashing letter
                raise InvalidWord(f"{word[0]} clashes with another word")

            grid[y][x] = letter
            # Only move if we're not at the last letter
            if index < len(word[0]) - 1:
                if word[1] == "N":
                    y -= 1
                elif word[1] == "S":
                    y += 1
                elif word[1] == "E":
                    x += 1
                elif word[1] == "W":
                    x -= 1

    return True


def calculate_score(wordlist: List[Tuple[str, str]]) -> int:
    """
    Calculate the score of the wordlist
    """
    score = 0
    for word in wordlist:
        score += len(word[0])
    
    return score


def instructions() -> None:
    print_color("""
██     ██  ██████  ██████  ██████   ██████  ██████  ██ ██████  
██     ██ ██    ██ ██   ██ ██   ██ ██       ██   ██ ██ ██   ██ 
██  █  ██ ██    ██ ██████  ██   ██ ██   ███ ██████  ██ ██   ██ 
██ ███ ██ ██    ██ ██   ██ ██   ██ ██    ██ ██   ██ ██ ██   ██ 
 ███ ███   ██████  ██   ██ ██████   ██████  ██   ██ ██ ██████  
 """, color="blue")
    print("Fill the grid with words. One point per letter in each word.")
    print("")
    print_color("Each word MUST:", color="green")
    print("* Start with the last letter of the previous word")
    print("* Be in the dictionary")
    print("* Fit on the grid")
    print("* Cannot clash with other letters already on the grid")
    print("* Not repeat.")
    print("")
    print_color("Here's what you can do:", color="green")
    print("* First letter is chosen at random in a random location on the grid")
    print("* Words can go North, South, East or West from the starting letter")
    print("* Words can overlap in any direction")
    print("")


def render_grid(seed: Tuple[str, Tuple[int, int]], wordlist: List[Tuple[str, str]]) -> None:
    """
    Render the wordlist and seed letter
    """
    # Initialise the grid
    grid = [ [Settings.filler] * Settings.grid_width for _ in range(Settings.grid_height)]

    # Set the seed in case there are no words in the list
    grid[seed[1][1]][seed[1][0]] = seed[0]

    # Place each word in the grid starting with the seed location
    x, y = seed[1]
    for word in wordlist:
        for index, letter in enumerate(word[0]):
            grid[y][x] = letter
            # Only move if we're not at the last letter
            if index < len(word[0]) - 1:
                if word[1] == "N":
                    y -= 1
                elif word[1] == "S":
                    y += 1
                elif word[1] == "E":
                    x += 1
                elif word[1] == "W":
                    x -= 1

    for row_index, row in enumerate(grid):
        for col_index, col in enumerate(row):
            if row_index == y and col_index == x:
                print_color(col, color="blue", end="")
            elif row_index == seed[1][1] and col_index == seed[1][0]:
                print_color(col, color="green", end="")
            else:
                print(f"{col}", end="")

        print("")

    print("")

def render_wordlist(wordlist: List[Tuple[str, str]]) -> None:
    foreground = "white"
    for word in wordlist:
        print_color(f"{word[0]} ({len(word[0])}) ", color=foreground, end="")
        foreground = "white" if foreground == "cyan" else "cyan"

    print("")

def main():
    """
    A word grid game
    * Present the user with a grid
    * A single random letter is placed at a random place on the grid
    * Users enter a word starting with that letter
    * (1) Word must fit in the grid
    * Word can go in any major cardinal direction (N, S, E, W)
    * Single point per letter
    * Next word must start with the last letter of the previous word
    * Repeat to (1) until no more words in the dictionary can fit the space
        * Words can overlap other words
        * No repeats
    """
    # From the date, get the following three values
    # A number between 1 and 26
    # A number between 0 and GRID_WIDTH
    # A number between 0 and GRID_HEIGHT
    seed = calculate_seed()
    wordlist = []
    Settings.load_dictionary()
    instructions()
    while True:
        try:
            render_grid(seed, wordlist)
            render_wordlist(wordlist)
            # Grab some input and validate
            last_letter = seed[0]
            if len(wordlist) > 0:
                last_letter = wordlist[-1][0][-1]

            new_word = ""
            while new_word == "":
                new_word = input(f"(score: {calculate_score(wordlist)}) Enter a word (Q=QUIT): {last_letter}").upper()

            if new_word == "Q":
                break
            new_word = f"{last_letter}{new_word}"
            direction = input("Enter direction (NSEW): ").upper()
            print("")
            print("")
            if direction not in ["N", "S", "E", "W"]:
                print_color(f"{direction} is not a valid direction", "red")
                continue
            temp_wordlist = wordlist.copy()
            temp_wordlist.append((new_word, direction))
            validate(seed, temp_wordlist)
            wordlist = temp_wordlist
        except InvalidWord as iwl:
            print_color(iwl, "red")

if __name__ == "__main__":
    main()
