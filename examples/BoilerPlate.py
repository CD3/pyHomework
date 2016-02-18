#! /bin/env python
import os, tempfile
from pyHomework import *


e = EquationsCollection()
s = e.s
c = ConstantsCollection(units, 3) # all constants to 3 sig figs
e.set_constants(c)

ass  = HomeworkAssignment()
ass.add_quiz()
quiz = ass.get_quiz()

courseName = "UNKNOWN"
semester   = "UNKNOWN"
module     = "UNKNOWN"


def Setup(_file_):
  absfilename =  os.path.abspath( _file_ )
  filename = os.path.basename( absfilename )
  absdirname = os.path.dirname( absfilename )

  #configure the title, header, and footer that will be generated
  #each of these have a default, so they can be left out
  global ass
  global quiz
  global courseName
  global semester
  global module

  courseName = GetCourseName(absfilename)
  semester   = GetSemester(absfilename)
  module     = GetModule(absfilename)

  ass.config( {"title" : "Module %s Homework" % module
              ,"LH" : "%s - %s" % (courseName,semester)
              ,"CH" : "FHSU"
              ,"RH" : 'Mod %s' % module
              ,"LF" : ""
              ,"CF" : ""
              ,"RF" : "Powered by \LaTeX" } )

def Build():
  # build a PDF and Bb quiz
  # make sure to get the basename before we change directories
  global ass
  global courseName,module

  basename = ("%s-HW_%s" % (courseName,module)).replace(' ', '_')

  workdir = '_'+module
  if not os.path.exists( workdir ):
    os.makedirs( workdir )
  os.chdir( workdir )

  # # this will create the pdf
  ass.build_PDF(basename+'.pdf')
  # # this will create a yaml file that can be parsed by BbQuiz.py to generate a blackboard quiz.
  ass.write_quiz_file(basename+'-Quiz.txt')


def GetSemester( filename ):
  '''Return the semester string, i.e. 'Spring 2015'.'''
  # some code to determine the semester
  return "Spring 2015"

def GetCourseName( filename ):
  '''Return the course name, i.e. 'Phys 212'.'''
  # some code to determine the course name
  return "Phys 212"

def GetModule( filename ):
  '''Return the module name, i.e. '01' or 'Electric_Charge'.'''
  # some code to determine the module name
  return "01"

