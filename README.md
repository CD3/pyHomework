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

BbQuiz.py
---------

BbQuiz.py reads a YAML file containing the description of a quiz and generates a .txt file that can be directly uploaded to Blackboard. This script provides several
benefits over creating quizzes in Blackboard directly, or using the Respondus Test Authoring Tool:

   - All questions are stored in a single YAML file, which is a simple format in human readable plain text.
      - Plain text files can be edited with your favorite text editor on any computer. No need for a special program.
      - Plain text files can be version controlled with tools like git or murcurial.
   - Support for numerical answer questions (the NUM) type.
      - Respondus could not create numerical questions for Blackboard, which was one of the main reasons I wrote the script now. It may support them now, I have not checked.
      - The range of accepted values is specified as a percentage. By default, a 1% range is used.

BbQuiz.py also has a few unique fetures that I have not found anywhere else:

   - The Mako template engine (http://www.makotemplates.org/) is used to pre-process the YAML input file,
     which allows for some amazing trick. For example, you can calculate
     the answer to a questions using python code and have the result inserted into the quiz.
   - Quiz questions can reference LaTeX labels, which will be replaced in the generated Bb quiz.
     So for example, if your quiz is asking questions about a homework set
     that you created in LaTeX, you can label your questions in LaTeX, then
     references those labels in the quiz file. This way, if you add a question
     to your homework set, all of the labels in the quiz referring to specific
     questions will automatically be updated. Labels are
     extracted from a .aux file specified in the quiz file.
