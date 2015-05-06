pyHomework
==========

A set of python modules and scripts for creating homework problem sets, paper quizzes (with a key), and Blackboard quizzes.

What is it?
-----------

The scripts and module were developed to write quizzes and homework sets for physics classes. The scripts can read quizzes from a
YAML file and generate LaTeX documents or Blackboard quiz files. The main advantage being that the YAML files are easier to maintain,
but other features exist such as the ability to randomize both question and answer (for multiple choice questions) order as well as generating
a quiz key (for paper quizzes).

The module provides utilities for creating homework problem sets, and Blackboard quizzes to accompany these problem sets, in a python program. 
The primary benefit of using the module is the creation of quizzes to accompany homework set. The homework sets are generated using LaTeX, which
could just as easily be written directly using document templates. However, using the utilities provided by the module, a quiz can be generated that
references questions in the homework set, and the reference numbers will be automatically managed.
