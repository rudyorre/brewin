# CS 131 Fall 2022: Project Starter

Hey there! This is a template repository that contains the necessary boilerplate for [CS 131](https://ucla-cs-131.github.io/fall-22/)'s quarter-long project: making an interpreter. The project specs are as follows:

1. [Project 1 Spec](https://docs.google.com/document/d/17Q4EPgHLMlMuQABhmgTpk_Ggxij0DZwvPQO2uzVVPzk/)
2. [Project 2 Spec](https://docs.google.com/document/d/14cZ7s-RPDO3FvYCDFMlS_NrGSSPUmavSX0wzsN-yHDw/)
3. [Project 3 Spec](https://docs.google.com/document/d/1YCSxxlHnuMBALfGzZNcDeY-AemcWxOlFQKHxsARk1Tg/)

There are three stages to the project; students are currently at the third. Thus, this folder contains the necessary bootstrapping code:

- `intbase.py`, the base class and enum definitions for the interpreter
- a sample `readme.txt`, which should illustrate any known bugs/issues with the program (or, an "everything's good!")

As well as **canonical solutions for Project 1 and 2** (written by Carey):

- `interpreterv1.py`/`interpreterv2.py`: a top-level entrypoint: has some utility classes, finding the main function, the interpreter loop, and handlers for each token type
- `env_v1.py`/`env_v2.py`: manages the "environment" / state for a program - includes scoping
- `func_v1.py`/`func_v2.py`: manages and caches functions, types
- `tokenize.py`: tokenization logic

You do not have to use the canonical solutions for Project 3; in particular, since you didn't write the code, it may be confusing!

Some notes on your submission (for Project 3)

1. You **must have a top-level, versioned `interpreterv3.py` file** that **exports the `Interpreter` class**. If not, **your code will not run on our autograder**.
2. You may also submit one or more additional `.py` modules that your interpreter uses, if you decide to break up your solution into multiple `.py` files.

You can find out more about our autograder, including how to run it, in [its accompanying repo](https://github.com/UCLA-CS-131/fall-22-autograder).

## Licensing and Attribution

This is an unlicensed repository; even though the source code is public, it is **not** governed by an open-source license.

This code was primarily written by [Carey Nachenberg](http://careynachenberg.weebly.com/), with support from his TAs for the [Fall 2022 iteration of CS 131](https://ucla-cs-131.github.io/fall-22/).
