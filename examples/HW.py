#! /bin/env python
import sys
sys.path.append("../src")

from pyHomework import *
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


ass.add_question()
ass.add_text("Consider a ray of light that enters a piece of glass from air.")

ass.add_part()
ass.add_text("If the ray is incident on the glass perpendicular to the surface, by what angle will it be bent?")

ass.add_part()
# use a raw python string if you want to embed latex code. this will turn off string interpolation.
ass.add_text(r"If the ray is incident on the glass at an angle of \SI{45}{\degree} to the surface, by what angle will it be bent?")



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
ass.quiz_set_answer_value( SpeedOfLight )




ass.add_question()
ass.add_text("Will the speed of light be faster in glass or water?")

ass.add_quiz_question()
# HomeworkAssignment only provides a helper function for Numerical questions types. The answer for all other question types are
# passes in as dictionaries correctly formatted for BbQuiz.py. Here is a multiple choice answer.
ass.quiz_add_answer( {'choices' : [ 'faster'
                                , '*slower'
                                , 'it is not possible to tell'
                                ] } )
# some quiz questions may require some special instructions in order to remove ambiguity in the question.
ass.quiz_add_instruction("Assume crown glass")


# this will create the pdf
ass.build_PDF('HW_Example-Problem_Set')
# this will create a yaml file that can be parsed by BbQuiz.py to generate a blackboard quiz.
ass.build_quiz('HW_Example-Quiz')
