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

The starting letter and its position will change once a day.

Installing
==========

Linux ELF only at this stage. The ELF can be found in the release section of the repository.

You will need to enable the execute attribute on the file. Then:

`./wordgrid`

Development
===========

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

TODO
====

Public score posting. This is