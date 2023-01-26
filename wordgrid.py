#!/usr/bin/env python3
import sys
import os
import io
from string import ascii_uppercase
from random import choice, randint, seed
from typing import Tuple, List
from zipfile import ZipFile
from datetime import date
"""
Word grid game
"""


class Settings:
    grid_width: int = 10
    grid_height: int = 10
    dictionary: List[str] = []
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
        Args:
            None

        Returns:
            bool: Current terminal supports ANSI colour
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
                import colorama  # noqa: F401
                cls._color = True
            except (ImportError, OSError):
                pass

        return cls._color

    @classmethod
    def load_dictionary(cls) -> None:
        """
        Load the dictionary from a Zip file
        Args:
            None

        Returns:
            None
        """
        mod_path = os.path.dirname(os.path.abspath(__file__))
        with ZipFile(os.path.join(mod_path, "english_dic.zip")) as dic_zip:
            with io.TextIOWrapper(
                dic_zip.open("english_dic.txt"), encoding="utf-8"
            ) as dic_handle:
                cls.dictionary = dic_handle.read().splitlines()

        """
        Now reduce the dictionary by discarding all words greater than the
        maximum grid size
        """
        max_length = max(Settings.grid_width, Settings.grid_height)
        cls.dictionary = [
            word for word in cls.dictionary if len(word) <= max_length
        ]

    @classmethod
    def empty_grid(cls) -> List[List[str]]:
        """
        Returns an empty, pre-allocated grid based on the settings
        Args:
            None

        Returns:
            list: A 2D list of the filler character
        """
        return [[cls.filler] * cls.grid_width for _ in range(cls.grid_height)]


def print_color(text: str, color: str, end="\n") -> None:
    """
    Attempt to print colour text to the terminal. Checking for ANSI
    Args:
        text (str): Text to print
        color (str): Colour name
        end (str): String end to pass to print

    Returns:
        None
    """
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
    """
    Exception used to capture invalid words for reasons
    """
    pass


def calculate_seed() -> Tuple[str, Tuple[int, int]]:
    """
    Using the current date, calculate the letter and coordinates
    Args:
        None

    Returns:
        (tuple, str): A single letter
        (tuple, Tuple, int): The coordinates of the letter
    """
    seed((date.today() - date(1970, 1, 1)).days)  # Seed it up
    return ("A", (5, 5))
    return (
        choice(ascii_uppercase),
        (
            randint(0, Settings.grid_width - 1),
            randint(0, Settings.grid_height - 1)
        )
    )


def validate(
    seed: Tuple[str, Tuple[int, int]],
    wordlist: List[Tuple[str, str]]
) -> None:
    """
    Validate the wordlist:
    * Word starts with the last letter of the previous word
    * Words fit in grid
    * No repeat words
    * Letters do not clash with letters already in the grid
    * Word not in the dictionary
    Raises an InvalidWord exception if something isn't right
    Args:
        seed (tuple): Containing the seed letter and starting coordinates
        wordlist (list): A list of words with their direction

    Returns:
        None
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
            raise InvalidWord(f"{word[0]} falls outside of the grid")
        if not 0 <= y <= Settings.grid_height - 1:
            raise InvalidWord(f"{word[0]} falls outside of the grid")

    # No repeat words
    repeatwordlist = [word[0] for word in wordlist]
    if len(wordlist) != len(set(repeatwordlist)):
        raise InvalidWord("Word already used")

    # Check for clashing letters
    fill_grid_from_wordlist(seed, wordlist)

    return True


def calculate_score(wordlist: List[Tuple[str, str]]) -> int:
    """
    Calculate the score of the wordlist
    Args:
        wordlist (list): List of word/direction pairs

    Returns:
        int: The total score from the wordlist
    """
    score = 0
    for word in wordlist:
        score += len(word[0])

    return score


def instructions() -> None:
    """
    Display the banner and instructions
    Args:
        None

    Returns:
        None
    """
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
    print("* Not repeat")
    print("* Not contain apostrophies.")
    print("")
    print_color("Here's what you can do:", color="green")
    print("* First letter is random at a random location on the grid")
    print("* Words can go North, South, East or West from the starting letter")
    print("* Words can overlap in any direction.")
    print("")


def fill_grid_from_wordlist(
    seed: Tuple[str, Tuple[int, int]],
    wordlist: List[Tuple[str, str]]
) -> Tuple[Tuple[int, int], List[List[str]]]:
    """
    Fill in a 2D list with the current wordlist
    Args:
        seed (tuple): Starting letter and position
        wordlist (list): A list of word/direction pairs

    Returns:
        tuple: The ending coordinates of the last word and the filled grid
    """
    grid = Settings.empty_grid()

    # Set the seed in case there are no words in the list
    grid[seed[1][1]][seed[1][0]] = seed[0]

    # Place each word in the grid starting with the seed location
    x, y = seed[1]
    letter = seed[0]
    for word in wordlist:
        for index, letter in enumerate(word[0]):
            if index > 0 and grid[y][x] not in [Settings.filler, letter]:
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

    return x, y, letter, grid


def render_grid(
    seed: Tuple[str, Tuple[int, int]],
    wordlist: List[Tuple[str, str]]
) -> None:
    """
    Render the wordlist and seed letter to the terminal highlighting
    the first and last letter
    Args:
        seed (tuple): Seed letter and coordinates

    Returns:
        None
    """
    last_x, last_y, _, grid = fill_grid_from_wordlist(seed, wordlist)

    for row_index, row in enumerate(grid):
        for col_index, col in enumerate(row):
            if row_index == last_y and col_index == last_x:
                print_color(col, color="blue", end="")
            elif row_index == seed[1][1] and col_index == seed[1][0]:
                print_color(col, color="green", end="")
            else:
                print(f"{col}", end="")

        print("")

    print("")


def render_wordlist(wordlist: List[Tuple[str, str]]) -> None:
    """
    Show the wordlist to the terminal
    Args:
        wordlist (list): Pairs of words and directions

    Returns:
        None
    """
    foreground = "white"
    for word in wordlist:
        print_color(f"{word[0]} ({len(word[0])}) ", color=foreground, end="")
        foreground = "white" if foreground == "cyan" else "cyan"

    print("")


def show_hint(
    seed: Tuple[str, Tuple[int, int]],
    wordlist: List[Tuple[str, str]]
) -> None:
    """
    Show a list of words that will fit in the available space
    Args:
        seed (tuple): The seed letter and position
        wordlist (list): A list of word/direction pairs

    Returns:
        None
    """
    print("The following words will fit...")
    last_x, last_y, last_letter, grid = fill_grid_from_wordlist(seed, wordlist)

    """
    Get the maximum length for each cardinal direction based on the position
    """
    n_max = last_y + 1
    s_max = Settings.grid_height - last_y
    w_max = last_x + 1
    e_max = Settings.grid_width - last_x

    e_mask = "".join(grid[last_y][last_x:])
    w_mask = "".join(grid[last_y][:w_max])[::-1]

    # Grab the whole vertical line
    v_line = "".join([line[last_x] for line in grid])
    n_mask = v_line[:n_max][::-1]
    s_mask = v_line[last_y:]

    """
    Take the word, overlay the mask, compare to see if it's different
    """
    def overlay(word: str, mask: str) -> str:
        return "".join(
            [
                letter if mask[index] == Settings.filler else mask[index]
                for index, letter in enumerate(word)
            ]
        )

    """
    Now check each direction
    """
    # Reduce the dictionary to words starting with the last letter
    words = [
        word for word in Settings.dictionary if word.startswith(last_letter)
    ]

    used_words = [word[0] for word in wordlist]

    hints = []
    for word in sorted(words, key=len, reverse=True):
        if word in used_words:
            continue
        if len(word) <= n_max and overlay(word, n_mask) == word:
            hints.append((word, "North"))
            continue
        if len(word) <= s_max and overlay(word, s_mask) == word:
            hints.append((word, "South"))
            continue
        if len(word) <= w_max and overlay(word, w_mask) == word:
            hints.append((word, "West"))
            continue
        if len(word) <= e_max and overlay(word, e_mask) == word:
            hints.append((word, "East"))
            continue

    """
    Show the top 20
    """
    if len(hints) == 0:
        print_color(
            "Cannot find words to fit the space available", color="red"
        )

    foreground = "white"
    for word in hints[:20]:
        print_color(
            f"{word[0]} ({word[1]}, {len(word[0])}pts) ",
            color=foreground,
            end=""
        )
        foreground = "white" if foreground == "cyan" else "cyan"

    print("")


def main() -> None:
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
    Args:
        None

    Returns:
        None
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
                new_word = input(
                    f"(score: {calculate_score(wordlist)}) "
                    f"Enter a word (Q=QUIT, !=HINT): {last_letter}"
                ).upper()

            if new_word == "Q":
                break
            if new_word == "!":
                show_hint(seed, wordlist)
                continue

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
