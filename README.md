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

PaperQuiz.py
---------

PaperQuiz.py reads a YAML file containing the description of a quiz and generates a PDF of the quiz. It has several useful features:

   - Randomize question order
   - Randomize answer order
   - Generate key

The YAML quiz description read by PaperQuiz.py is the same format read by BbQuiz.py, so it is possible to create a Blackboard and Paper version of the
same quiz.

Examples
========

Simple
------

Say you just want to write a short quiz that you can upload to Blackboard. First run `BbQuiz.py` with the `-e` option to generate an example quiz file:

    BbQuiz.py -e example_quiz.yaml

This will create a file named `example_quiz.yaml` in the current directory that includes examples of all question types that `BbQuiz.py` recognizes.

    # example_quiz.yaml


    configuration:
      randomize:
        questions: True
        answers: False
      special_chars:
        correct_answer : '*^'
      remote:
        web_root: 'http://scatcat.fhsu.edu/~user/'
        copy_root: 'ssh://user@scatcat.fhsu.edu/~/public_html'
        image_dir : 'images'

    questions:
      - 
        text: "(Multiple Choice) What is the correct answer?"
        answer:
          choices:
          - '*this is the correct answer'
          - 'this is not the correct answer'
          - 'this is also not the correct answer'

      - 
        text: "(Multiple Answers) What answers are correct?"
        answer:
          choices:
          - '*this is a correct answer'
          - 'this is not a correct answer'
          - '*this is also a correct answer'

      - 
        text: "(Ordered) Put these items in the correct order"
        answer:
          ordered :
          - 'first'
          - 'second'
          - 'third'
      - 
        text: "(Numerical Answer) What is the correct number?"
        answer:
          value : 7

      - 
        text: "(Numerical Answer) What is the correct number, plus or minus 20%?"
        answer:
          value : 7
          uncertainty: 20%
      - 
        text: "(True/False) Is the answer True?"
        answer: True
      - 
        text: "(Image Example) Can you see the picture?"
        image: './picture.png'
        answer:
          choices:
            - '*yes'
            - 'no'

Now you can create your quiz by copy-and-pasting the example questions and modifying them. After you done, just run `BbQuiz.py` on the YAML file and it will create a text file
that can be uploaded to Bloackboard. Running `BbQuiz.py` on the example file directly produces the following

    > BbQuiz.py example_quiz.yaml

    > cat example_quiz.txt
    MA	(Multiple Answers) What answers are correct?	this is a correct answer	correct	this is not a correct answer	incorrect	this is also a correct answer	correct
    MC	(Multiple Choice) What is the correct answer?	this is the correct answer	correct	this is not the correct answer	incorrect	this is also not the correct answer	incorrect
    MC	To answer this question, view the picture at http://scatcat.fhsu.edu/~user/images/picture.png by copying the link into your browser IN A NEW TAB (DO NOT USE THIS TAB). (Image Example) Can you see the picture?	yes	correct	no	incorrect
    TF	(True/False) Is the answer True?	true
    NUM	(Numerical Answer) What is the correct number?	7.00E+00	7.00E-02
    ORD	(Ordered) Put these items in the correct order	first	second	third
    NUM	(Numerical Answer) What is the correct number, plus or minus 20%?	7.00E+00	1.40E+00

Notice that the questions are not in the same order as they where in the YAML file. This is because BbQuiz.py has randomized them. Note too that the first Numerical Answer questions
had an uncertainty, even though none was specified in the YAML file. This is because `BbQuiz.py` assumes a 1% uncertainty if none is given.

`PaperQuiz.py` generates a PDF, and it reads the same file format as `BbQuiz.py`, so you can run it on the same YAML file

    > BbQuiz.py example_quiz.yaml

This will create a file named `example_quiz.pdf`. Not all question types really make sense for a paper quiz, but you get the idea. If you have a quiz consisting of multiple-choice, numerical answer, and True/False questions, you can
easily create a paper and online version of the quiz.
