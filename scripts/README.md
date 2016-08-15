# QuizGen

Generate Blackboard quizzes from simple, plain text files formatted similar to markdown.

## Description

`QuizGen` reads a quiz from simple text file formatted similar to mardown and generates a text file that can be uploaded to Blackboard.
Writing your quiz in markdown is more readable than the Blackboard text format, but `QuizGen` also provides support for embedding
images in your quiz as well math written in LaTeX.

**Basic Features/Benefits**
- Simple format based on markdown lists.
- Include images.
- Include math rendered from LaTeX code.
- Images (including math) are embedded directly into the quiz via the html img tab. No more broken image links on course copies.
- Numerical answers with units will automatically add an instruction at the end of the question indicating the units that the answer value should be in.
- Tolerance for numerical answers can be specified with a +/- syntax and will default to 1%.
- Your quizzes are stored in a human readable, open format and can easily be version controlled.
- Support for user-defined macros (advanced)

## Example

Here is a simple quiz file that demonstrates the basic features.

    title : Quiz
    configuration/make_key : True
    configuration/randomize/questions: True
    configuration/randomize/answers: False

    # this is a comment. comments are ignored

    # multiple choice questions are written with the possible
    # answeres listed below. the correct answer is marked with a ^
    1. (Multiple Choice) What is the correct answer?
       a. ^this is the correct answer
       b. this is not the correct answer
       c. this is also not the correct answer

    # more than one answer may be correct.
    2. (Multiple Answers) What answers are correct?
       a. ^this is a correct answer
       a. this is not a correct answer
       a. ^this is also a correct answer

    # numerical answer questions have a... numerical answer.
    # by default, a 1% tolerance will be used.
    1. (Numerical Answer) What is the correct number?
       answer : 7

    # the tolerance can be specified
    1. (Numerical Answer) Enter any number between 8 and 12.
       answer : 10 +/- 2

    # you can also put units in the answer. a statement that indicates what units the answer
    # should be given will automatically be generated and appended to the question.
    1. (Numerical Answer) How long is a football field?
       answer : 100 yd

    # images can be loaded
    1. Images can be included with the include graphics command: \includegraphics{./filename.png}
       They are embedded directly into the quiz file, so there is no chance of a broken link.
       a. ^yes
       b. no

    1. Image options are given in square brackets. \includegraphics[width="300"]{./filename.png}
       a. ^yes
       b. no

To generate a Blackboard formatted quiz file, run `QuizGen` with the name of this file as an argument (or just drag this file onto the `QuizGen` icon.

## Limitations

`QuizGen` is does not parse markdown (in fact, quizzes are stored in a dict that is can be represented directly in YAML), so it does *not* support the
markdown syntax for anything other than specifying a numbered list. 

## TODO

- Support other question types (ordered list, short answer, etc.)
- Add full markdown parsing
- Teach Dr. Deyo how to use (it's so simple)
