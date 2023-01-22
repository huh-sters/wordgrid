#!/usr/bin/env python3
import click
import os
import io
from string import ascii_uppercase
from random import choice, randint
from typing import Tuple, List
from zipfile import ZipFile
"""
Word grid game
"""

GRID_WIDTH = 10
GRID_HEIGHT = 10

DICTIONARY = []

FILLER = "."

class InvalidWordList(Exception):
    pass


def load_dictionary():
    global DICTIONARY
    mod_path = os.path.dirname(os.path.abspath(__file__))
    with ZipFile(os.path.join(mod_path, "english_dic.zip")) as dic_zip:
        with io.TextIOWrapper(dic_zip.open("english_dic.txt"), encoding="utf-8") as dic_handle:
            DICTIONARY = dic_handle.read().splitlines()


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
        if word[0] not in DICTIONARY:
            raise InvalidWordList(f"{word[0]} is not in the dictionary")
        if word[0][0] != last_letter:
            raise InvalidWordList(f"{word[0]} does not start with {last_letter}")
        last_letter = word[0][-1]
        if word[1] == "N":
            y -= len(word[0]) - 1
        elif word[1] == "S":
            y += len(word[0]) - 1
        elif word[1] == "E":
            x += len(word[0]) - 1
        elif word[1] == "W":
            x -= len(word[0]) - 1
        if not 0 <= x <= GRID_WIDTH - 1:
            raise InvalidWordList(f"{word[0]} falls outside of the x grid")
        if not 0 <= y <= GRID_HEIGHT - 1:
            raise InvalidWordList(f"{word[0]} falls outside of the y grid")

    # No repeat words
    repeatwordlist = [word[0] for word in wordlist]
    if len(wordlist) != len(set(repeatwordlist)):
        raise InvalidWordList(f"Repeat word found")

    # Check for clashing letters
    # Initialise the grid
    grid = [ [FILLER] * GRID_WIDTH for _ in range(GRID_HEIGHT)]

    # Set the seed in case there are no words in the list
    grid[seed[1][1]][seed[1][0]] = seed[0]

    # Place each word in the grid starting with the seed location
    x, y = seed[1]
    for word in wordlist:
        for index, letter in enumerate(word[0]):
            if index > 0 and grid[y][x] not in [FILLER, letter]:  # Clashing letter
                raise InvalidWordList(f"{word[0]} clashes with another word")

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


def instructions():
    click.echo(""")
██     ██  ██████  ██████  ██████   ██████  ██████  ██ ██████  
██     ██ ██    ██ ██   ██ ██   ██ ██       ██   ██ ██ ██   ██ 
██  █  ██ ██    ██ ██████  ██   ██ ██   ███ ██████  ██ ██   ██ 
██ ███ ██ ██    ██ ██   ██ ██   ██ ██    ██ ██   ██ ██ ██   ██ 
 ███ ███   ██████  ██   ██ ██████   ██████  ██   ██ ██ ██████  
 """)
    click.echo("Fill the grid with words. One point per letter in each word.")
    click.echo("Each word MUST:")
    click.echo("* Start with the last letter of the previous word")
    click.echo("* Be in the dictionary")
    click.echo("* Fit on the grid")
    click.echo("* Cannot clash with other letters already on the grid")
    click.echo("* Not repeat.")
    click.echo("")
    click.echo("Here's what you can do:")
    click.echo("* First letter is chosen at random in a random location on the grid")
    click.echo("* Words can go North, South, East or West from the starting letter")
    click.echo("* Words can overlap in any direction")


def render_grid(seed: Tuple[str, Tuple[int, int]], wordlist: List[Tuple[str, str]]):
    """
    Render the wordlist and seed letter
    """
    # Initialise the grid
    grid = [ [FILLER] * GRID_WIDTH for _ in range(GRID_HEIGHT)]

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

    for row in grid:
        for col in row:
            click.echo(f"{col}", nl=False)
        click.echo("")


@click.command()
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
    global DICTIONARY
    seed = (choice(ascii_uppercase), (randint(0, GRID_WIDTH - 1), randint(0, GRID_HEIGHT - 1)))
    wordlist = []
    load_dictionary()
    instructions()
    while True:
        try:
            render_grid(seed, wordlist)
            # Grab some input and validate
            last_letter = seed[0]
            if len(wordlist) > 0:
                last_letter = wordlist[-1][0][-1]

            new_word = input(f"(score: {calculate_score(wordlist)}) Enter a word (Q=QUIT): {last_letter}").upper()
            if new_word == "Q":
                break
            new_word = f"{last_letter}{new_word}"
            direction = input("Enter direction (NSEW): ").upper()
            temp_wordlist = wordlist.copy()
            temp_wordlist.append((new_word, direction))
            validate(seed, temp_wordlist)
            wordlist = temp_wordlist
        except InvalidWordList as iwl:
            click.echo(iwl)

if __name__ == "__main__":
    main()
