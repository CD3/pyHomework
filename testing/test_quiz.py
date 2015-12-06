
from pyHomework.Quiz import Quiz
from pyHomework.Answer import *
from pyErrorProp import *

def test_numerical_answer_value():

  q = 1.23456789
  a = NumericalAnswer(q)
  assert a.quantity == '1.23E+00'
  assert a.value    == '1.23E+00'

  q = 13.579
  a = NumericalAnswer(q)
  assert a.quantity == '1.36E+01'
  assert a.value    == '1.36E+01'

  q = Q_(1.2345,'m')
  a = NumericalAnswer(q)
  assert a.quantity == '1.23E+00 meter'
  assert a.value    == '1.23E+00'

  q = Q_(12.345,'m/s')
  a.quantity = q
  assert a.quantity == '1.23E+01 meter / second'
  assert a.value    == '1.23E+01'

  q = Q_(1.3579,'m/s^2')
  a.quantity = q
  assert a.quantity == '1.36E+00 meter / second ** 2'
  assert a.value    == '1.36E+00'
  a.sigfigs = 4
  assert a.quantity == '1.358E+00 meter / second ** 2'
  assert a.value    == '1.358E+00'


def test_numerical_answer_units():

  q = 1.23456789
  a = NumericalAnswer(q)
  assert a.units == ''

  q = Q_(1.23456789,'m')
  a = NumericalAnswer(q)
  assert a.units == 'meter'

  a.units = 'foot'
  assert a.units == 'meter'

  a.quantity = 1.2
  assert a.units == 'foot'

def test_numerical_answer_uncertainty():

  q = 1.23456789
  a = NumericalAnswer(q)
  assert a.uncertainty == '1.23E-02'
  a.uncertainty = '10%'
  assert a.uncertainty == '1.23E-01'
  a.uncertainty = 0.5
  assert a.uncertainty == '5.00E-01'
  a.quantity = Q_(2,'m/s')
  assert a.uncertainty == '5.00E-01'
  a.quantity = UQ_(2,0.01,'m/s')
  assert a.uncertainty == '1.00E-02'
  a.quantity = Q_(2,'m/s')
  assert a.uncertainty == '5.00E-01'


def test_multiple_choice_answer():
  a = MultipleChoiceAnswer()
  a.add_choice('one')
  a.add_choice('*two')
  a.add_choice('three')

  assert str(a) == 'two'

  a.add_choice('*four')

  assert str(a) == 'two, four'

def test_written_answer():
  pass

def test_latex_answer():
  pass

def test_question_add_text():
  q = Quiz.Question()

  q.add_text( "Second sentence." )
  q.add_text( "Third")
  q.add_text( "sentence." )
  q.add_text( "First sentence.", prepend=True )
  q.add_text( "{x}" )
  q.add_text( "${x}" )
  q.format_text( x = "Fifth sentence." )
  q.format_text( x = "Fourth sentence.", formatter='format' )

  assert q.text == "First sentence. Second sentence. Third sentence. Fourth sentence. Fifth sentence."

def test_question_add_instruction():
  q = Quiz.Question()
  q.add_instruction("text.")
  q.add_instruction("Instruction", prepend=True)

  assert q.instructions == "Instruction text."

def test_question_add_text_and_instruction():
  q = Quiz.Question()
  q.add_text("Question text.")
  q.add_instruction("Instruction text.")

  assert q.question == "Question text. Instruction text."

  q.prepend_instructions = True
  assert q.question == "Instruction text. Question text."

  q.prepend_instructions = False
  assert q.question == "Question text. Instruction text."

def test_question_set_text():
  q = Quiz.Question()

  q.add_text( "one" )
  q.add_text( "two")
  q.add_text( "three" )

  q.set_text( "four" )

  assert q.question == "four"

def test_question_set_instruction():
  q = Quiz.Question()

  q.add_instruction( "one" )
  q.add_instruction( "two")
  q.add_instruction( "three" )

  q.set_instruction( "four" )

  assert q.question == "four"

