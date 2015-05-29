#! /bin/env python
import sys, math
sys.path.insert(0,"../src")

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

# add some quiz questions

ass.add_quiz_question()
ass.quiz_add_text("What is the speed of light?")
ass.quiz_set_answer_value( SpeedOfLight )

diam = Q_(2.5, "cm")
ass.add_quiz_question()
ass.quiz_add_text("What is the area of a circle with diameter %s?" % diam)
ass.quiz_set_answer_value( math.pi * diam * diam / 4 )


ass.build_quiz('Quiz_Example-Quiz')
