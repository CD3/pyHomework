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

Installing
----------

To install the `pyHomework` module and program scripts, run the `setup.py` script with the `install` argument,

  > sudo python setup.py install

The module and scripts depend on a few python modules that may not be installed by default, but can easily be installed via `pip`,

  > sudo pip install pyyaml cerberus dpath pypdf sympy numpy pint

The scripts that generate PDF files (for paper quizzes or problem sets) do so by writing `LaTeX` and compiling it with `latexmk`. You therefore
must install `latexmk` to use these scripts. On Debian-based distros (Ubuntu, Mint, etc.) you can install `latexmk` with `apt-get`:

  > sudo apt-get install latexmk

In addition to this, the generated `LaTeX` files use a few packages that may not be installed by default,
most notibly the `siunitx` package that formats quantities with units correctly. You need to install these packages before attempting to compile
the generated `LaTeX`. On Debian-based distributions, install the required packages with the following command:

  > sudo apt-get install texlive-science texlive-latex-extras
 

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

The `HomeworkAssignment` Class
----------------------------

The `pyHomework` module contains a `HomeworkAssignment` class that can be used to build a homework assignment in a Python program. The interface
works like a stack. You create a `HomeworkAssignment` object and then begin adding questions, figures, quiz questions, etc. The class provides
a set of member functions for adding text to, setting answers, settings units (and more) to questions, and these member act on the last question
(or question part) in the stack.

The most powerful feature is the ability to generate Blackboard quizzes for the homework assignment. You add quiz questions after the homework
questions they refer to and the `HomeworkAssignment` takes care of automatically inserting the correct label into the question so that it
will contain the question number. In addition to this, the `HomeworkAssignment` class supports the `pint` module, so that if you set the answer to a
quiz question and the answer has units, the quiz question that is generated will specify what units to give the answer in.

Because the homework assignment is built in a python program, you are free to generate the homework assignment and quiz however you want (you could
write a program to read a YAML file for example). In fact, you have have the full Python language, and any other modules you want to use, at your
disposal for computing the answers to quiz questions. So, for example, you could write a function to solve for the currents through some
system of resistors using a matrix solver. Then if you change the individual resistors, your answer will automatically be updated.

Examples
========

Simple Blackboard Quiz
----------------------

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

Creating a homework assignment
------------------------------

Here is a demonstration of how the `HomeworkAssignment` class can be used:used


    #! /bin/env python
    import sys

    from HomeworkAssignment import *
    # shorthand for defining quantities withunits
    Q_ = units.Quantity

    # setting up some fundamental equations we will use

    di, do, f, m  = sy.symbols('d_i d_o f m')
    LensEquation  = sy.Eq( 1/di + 1/do , 1/f )
    MagEquation   = sy.Eq( m , -di / do )

    ni,nr,thi,thr = sy.symbols(r'n_i n_r \theta_i \theta_r')
    SnellsLaw     = sy.Eq( ni*sy.sin(thi), nr*sy.sin(thr) )


    # some constants
    SpeedOfLight         = Q_(2.99e8,"m/s")
    RefractiveIndexWater = 1.333


    # haha, just to amuse ourselves
    ass = HomeworkAssignment()

    #configure the title, header, and footer that will be generated
    #each of these have a default, so they can be left out
    ass.add_vars( {"title" : "the Title"
                 ,"LH" : "Left Header"
                 ,"CH" : "Center Header"
                 ,"RH" : "Right Header"
                 ,"LF" : "Left Footer"
                 ,"CF" : "Center Footer"
                 ,"RF" : "Right Footer" } )



    # start adding questions
    # the 'add_text' member function of HomeworkAssignment will
    # add text to the last question or part that # added.

    ass.add_question()
    ass.add_text("Does light travel faster or slower (compared to vacuum) in materials with a high refractive index?")

    ass.add_paragraph( Paragraph("Paragraphs can be used to put some text between questions") )

    ass.add_question()
    ass.add_text("Consider a ray of light that enters a piece of glass from air.")

    ass.add_part()
    ass.add_text("If the ray is incident on the glass perpendicular to the surface, by what angle will it be bent?")

    ass.add_paragraph( Paragraph("but they cannot go between parts.") )

    ass.add_part()
    # use a raw python string if you want to embed latex code. this will turn off string interpolation.
    ass.add_text(r"If the ray is incident on the glass at an angle of \SI{45}{\degree} to the surface, by what angle will it be bent?")


    # add a figure
    ass.add_figure( 'picture.png' )
    ass.set_figure_data( 'label', 'fig:pic1' )
    ass.set_figure_data( 'caption', 'This is an example figure.' )

    ass.add_question()
    ass.add_text("What is the speed of light in water?")

    # add a quiz question
    ass.add_quiz_question()
    # we have to use a different member function because this will add some special sauce for quiz questions.
    # the most useful thing it does is automatically creates a reference to the last question or part that will appear
    # in the Blackboard quiz that gets generated. Every questions in the generated quiz will begin with
    #'For problem #X: '
    # BbQuiz.py uses the LaTeX .aux file that is created when we build the PDF so that all references will be the same
    # as those used by LaTeX.
    ass.quiz_add_text("What was the speed of light?")
    # we can use this helper function for setting numerical values. it will automatically create a
    # statement indicating the units that the answer should be given in.
    ass.quiz_set_answer( NumericalAnswer(SpeedOfLight) )




    ass.add_question()
    ass.add_text("Will the speed of light be faster in:")

    ass.add_part()
    ass.add_text("glass or water?")

    ass.add_quiz_question()
    ass.quiz_add_text("which material will it be faster in?")
    # HomeworkAssignment only provides a helper function for Numerical questions types. The answer for all other question types are
    # passes in as dictionaries correctly formatted for BbQuiz.py. Here is a multiple choice answer.
    answer = MultipleChoiceAnswer()
    answer.add_choice( 'faster' )
    answer.add_choice( '*slower' )
    answer.add_choice( 'it is not possible to tell' )
    ass.quiz_set_answer( answer )

    # some quiz questions may require some special instructions in order to remove ambiguity in the question.
    ass.quiz_add_instruction("Assume crown glass.")

    # add another figure
    ass.add_figure( 'picture.png' )
    ass.set_figure_data( 'label', 'fig:pic2' )
    ass.set_figure_data( 'caption', 'This is another example figure.' )
    ass.set_figure_data( 'options', 'width=2in' )


    ass.add_paragraph( Paragraph(r'''\vspace{1in}If you need more spacing,
      
    just embed latex spacing commands.''') )
    for i in range(10):
      ass.add_question()
      ass.add_text("These questions are just to fill the page...")
      ass.add_part()
      ass.add_text("to show how page breaks work...")
      ass.add_part()
      ass.add_text("questions should not be split across pages...")
      ass.add_part()
      ass.add_text("the main question and all parts should appear on the same page.")
      ass.add_part()
      ass.add_text(r"so, yea. Figures \ref{fig:pic1} and \ref{fig:pic2} are the same.")


    # we can just write the latex and yaml quiz
    #ass.write_latex('test-latex.tex')
    #ass.write_quiz('test-latex.yaml')

    # or build a PDF and Bb quiz

    # this will create the pdf
    ass.build_PDF('HW_Example-Problem_Set')
    # this will create a yaml file that can be parsed by BbQuiz.py to generate a blackboard quiz.
    ass.build_quiz('HW_Example-Quiz')
