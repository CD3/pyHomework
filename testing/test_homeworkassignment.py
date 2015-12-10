from pyHomework import *
from pyHomework.Answer import *
import pytest

def Close( a, b, tol = 0.001 ):
    if isinstance(a,int):
        a = float(a)
    if isinstance(b,int):
        b = float(b)
    return (a - b)**2 / (a**2 + b**2) < 4*tol*tol


needsporting = pytest.mark.skipif(True, reason="Need to port to new Answer/Question/Quiz classes")

@needsporting
def test_quiz():
  ass = HomeworkAssignment()


  ass.add_question()
  ass.add_text("Question \#1")
  ref1 = ass.get_last_ref()
  
  ass.add_part()
  ass.add_text("Question \#1, Part a")
  ref1a = ass.get_last_ref()

  ass.add_part()
  ass.add_text("Question \#1, Part b")


  ass.add_question()
  ass.add_text("Question \#2")
  
  ass.add_part()
  ass.add_text("Question \#2, Part a")

  ass.add_part()
  ass.add_text("Question \#2, Part b")
  ref2b = ass.get_last_ref()


  ass.add_question()
  ass.add_text(r"Question \#3 references \ref{%s}, \ref{%s}, \ref{%s}." % (ref1,ref1a,ref2b) )

  ass.add_quiz_question()
  ass.quiz_add_text("What is the answer?")
  Answer = Q_(123456789,'N')
  ass.quiz_set_answer( NumericalAnswer( Answer ) )


  ass.add_part()
  ass.add_text(r"Question \#3, Part b, also references \ref{${r1}}, \ref{${r1a}}, \ref{${r2b}}.")
  ass.format_text( r1=ref1, formatter='template' )
  ass.format_text( r1a=ref1a, r2b=ref2b, formatter='template' )

  ass.add_quiz_question()
  ass.quiz_add_text("What is the answer?")
  Answer = UQ_(123456789,40,'N')
  ass.quiz_set_answer( NumericalAnswer( Answer ) )

  ass.write_latex('test.tex')
  ass.write_quiz('test-quiz.yaml')

  ass.build_PDF('test.pdf')

@needsporting
def test_numerical_answer():
  import pint
  units = pint.UnitRegistry()
  Q_ = units.Quantity
  M_ = units.Measurement

  Answer = Q_(1.2345,'m/s')
  a = NumericalAnswer(Answer)
  d = a.dict()

  assert d['value'] == '1.23E+00'
  assert d['uncertainty'] == '1%'
  assert d['unit'] == 'meter / second'


  Answer = M_(1.2345,0.034,'m/s')
  a = NumericalAnswer(Answer)
  d = a.dict()

  assert d['value'] == '1.234E+00'
  assert d['uncertainty'] == '0.034E+00'
  assert d['unit'] == 'meter / second'


  Answer = Q_(123.45,'m/s')
  a = NumericalAnswer(Answer)
  d = a.dict()

  assert d['value'] == '1.23E+02'
  assert d['uncertainty'] == '1%'
  assert d['unit'] == 'meter / second'


  Answer = M_(123.45,3.4,'m/s')
  a = NumericalAnswer(Answer)
  d = a.dict()

  assert d['value'] == '1.234E+02'
  assert d['uncertainty'] == '0.034E+02'
  assert d['unit'] == 'meter / second'


  Answer = Q_(0.00012345,'m/s')
  a = NumericalAnswer(Answer)
  d = a.dict()

  assert d['value'] == '1.23E-04'
  assert d['uncertainty'] == '1%'
  assert d['unit'] == 'meter / second'


  Answer = M_(0.00012345,0.0000034,'m/s')
  a = NumericalAnswer(Answer)
  d = a.dict()

  assert d['value'] == '1.234E-04'
  assert d['uncertainty'] == '0.034E-04'
  assert d['unit'] == 'meter / second'

