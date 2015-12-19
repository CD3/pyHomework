pyHomework
==========

`pyHomework` allows you to write quizzes, problem sets, and quizzes about problem sets in Python. Why would you want to do this?

  - Writing code is funner than writing homework assignments.
  - Answers to questions can be calculated in python.
  - Updating numbers for a question is trivial, just update the variable storing the number.

`pyHomework` was born when I decided to start assigning standalone problem sets for my physics classes and give online quizzes (with Blackboard) over the problem set that could
be graded automatically. I wanted a way to assign a "traditional" physics problem set but I could not grade every problem I assigned to a class of 30 - 40 students and needed
a way to motivate the students to do the homework. Creating a
problem set is not difficult, but giving a quiz over the problem set requires a set of solutions. Not only that, but the quiz questions do not need to restate the entire problem that was
on the problem set, they just need to ask for some information about the problem's solution. So the quiz questions need to reference problem numbers, and this turned out to be the
difficult part. It is *very* easy to make a mistake and reference the wrong question number, which just confuses everybody involved. Even if you manage to get the references right
the first time, it is difficult to add or change questions to the problem set in the future because the problem numbers may change and the quiz has to be updated. To top it all off,
creating a quiz in Blackboard is a *pain*.

What eventually became `pyHomework` started off as a Blackboard quiz generator. I wrote a simple script that would read quizzes in YAML format and generate a text file that could be
uploaded to Blackboard (the text file format is difficult to edit by hand). Now, it is possible to write a python program that will generate a problem set as a PDF document (using LaTeX)
and a quiz file that can be uploaded to Blackboard. It tries to be flexible while automating much of the repetitive tasks associated with writing a homework assignment.


Examples
---------

`pyHomework` has recently been rewritten and supports a new interface. Eamples to come.
