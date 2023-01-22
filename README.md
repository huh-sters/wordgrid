Wordgrid
========

Terminal based word game

Fill the grid with words. One point per letter in each word.
Each word MUST:
* Start with the last letter of the previous word
* Be in the dictionary
* Fit on the grid
* Cannot clash with other letters already on the grid
* Not repeat.

Here's what you can do:
* First letter is chosen at random in a random location on the grid
* Words can go North, South, East or West from the starting letter
* Words can overlap in any direction

Installing
==========

Linux ELF only at this stage.

To setup for development you will need Python 3.10 and a copy of PDM installed

To install the dependencies

`pdm install`

To build the single file distribution

`pdm run clean`
`pdm run build`

ELF lives in the `dist` folder.

Running
=======

From the terminal in the projects folder

`pdm run wordgrid`

