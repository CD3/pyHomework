
import pytest

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

def test_numerical_answer_bb_emitter():
  q = 1.23456789
  a = NumericalAnswer(q)
  bb = a.emit('bb')
  assert bb == '1.23E+00\t1.23E-02'

  q = Q_(1.3579,'m/s^2')
  a = NumericalAnswer(q)
  bb = a.emit('bb')
  assert bb == '1.36E+00\t1.36E-02'
  a.sigfigs = 4
  bb = a.emit('bb')
  assert bb == '1.358E+00\t1.358E-02'


  q = UQ_(1.3579, 0.89, 'm/s^2')
  a = NumericalAnswer(q)
  bb = a.emit('bb')
  assert bb == '1.36E+00\t8.90E-01'

def test_answer_emitter_exceptions():
  q = 1.23456789
  a = NumericalAnswer(q)
  with pytest.raises(RuntimeError) as e:
    a.emit('undefined')
  assert str(e.value) == "Unknown emitter type 'undefined' given."


  a = MultipleChoiceAnswer()
  with pytest.raises(RuntimeError) as e:
    a.emit('undefined')
  assert str(e.value) == "Unknown emitter type 'undefined' given."

def test_answer_custom_emitters():
  def num_emit(a):
    return "Answer is: %s" % a.quantity

  q = 1.23456789
  a = NumericalAnswer(q)
  text = a.emit(num_emit)
  assert text == "Answer is: 1.23E+00"

  def mc_emit(a):
    return "Answer is: '%s'" % a._choices[ a._correct.copy().pop() ]

  a = MultipleChoiceAnswer()
  a.add_choices('''
  not correct
  *this one
  not this one
  ''')
  text = a.emit(mc_emit)
  assert text == "Answer is: 'this one'"

def test_multiple_choice_answer():
  a = MultipleChoiceAnswer()
  a.add_choice('one')
  a.add_choice('*two')
  a.add_choice('three')

  assert str(a) == 'two'

  a.add_choice('*four')

  assert str(a) == 'two, four'

def test_multiple_choice_answer_bbquiz_emitter():
  a = MultipleChoiceAnswer()
  a.add_choice('one')
  a.add_choice('*two')
  a.add_choice('three')
  a.add_choice('*four')

  bbquiz = a.emit('bbquiz')
  assert 'choices' in bbquiz
  assert bbquiz['choices'][0] == 'one'
  assert bbquiz['choices'][1] == '*two'
  assert bbquiz['choices'][2] == 'three'
  assert bbquiz['choices'][3] == '*four'

def test_multiple_choice_answer_bb_emitter():
  a = MultipleChoiceAnswer()
  a.add_choice('one')
  a.add_choice('*two')
  a.add_choice('three')
  a.add_choice('*four')

  bb = a.emit('bb')

  assert bb == 'one\tincorrect\ttwo\tcorrect\tthree\tincorrect\tfour\tcorrect'

def test_written_answer():
  a = ShortAnswer('''Since A > B and B > C, A must also be > C.''')

  bb = a.emit('bb')
  assert bb == 'Since A > B and B > C, A must also be > C.'

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


def test_question_with_numerical_answer():
  q = Quiz.Question()

  l = Q_(1.5,'m')
  w = Q_(2.5,'m')
  # print l*w
  q.add_text("What is the area of a {l} x {w} square?")
  q.format_text( l=l, w=w, formatter='format' )
  q.set_answer( NumericalAnswer( l*w ) )

  text = q.emit('bb')

  assert text == 'NUM\tWhat is the area of a 1.5 meter x 2.5 meter square?\t3.75E+00\t3.75E-02'


def test_question_with_mc_answer():
  q = Quiz.Question()

  q.add_text("The answer is c... its always c.")
  a = MultipleChoiceAnswer()
  a.add_choices('''
  this is not the answer you are looking for.
  nope.
  *this is it!
  really?
  ''')
  q.set_answer( a )

  text = q.emit('bb')

  assert text == 'MC\tThe answer is c... its always c.\tthis is not the answer you are looking for.\tincorrect\tnope.\tincorrect\tthis is it!\tcorrect\treally?\tincorrect'

def test_question_mc_ordering():
  q = Quiz.Question()

  q.add_text("Question:")
  a = MultipleChoiceAnswer()
  a.add_choices('''
  a
  b
  *c
  d
  ''')
  q.set_answer( a )
  a.order = [1,0,3,2]

  text = q.emit('bb')

  assert text == 'MC\tQuestion:\tb\tincorrect\ta\tincorrect\td\tincorrect\tc\tcorrect'

def test_question_with_ma_answer():
  q = Quiz.Question()

  q.add_text("The answer is c... its always c.")
  a = MultipleChoiceAnswer()
  a.add_choices('''
  this is not the answer you are looking for.
  nope.
  *this is it!
  really?
  *oh...this one too.
  ''')
  q.set_answer( a )

  text = q.emit('bb')

  assert text == 'MA\tThe answer is c... its always c.\tthis is not the answer you are looking for.\tincorrect\tnope.\tincorrect\tthis is it!\tcorrect\treally?\tincorrect\toh...this one too.\tcorrect'

def test_question_emitter_exceptions():
  q = Quiz.Question()
  q.add_text("The answer is c... its always c.")
  with pytest.raises(RuntimeError) as e:
    q.emit('undefined')
  assert str(e.value) == "Unknown emitter type 'undefined' given."

def test_question_emitter_exceptions():
  def q_emit(q):
    return "Question: '%s'\nThe answer is irrelevent" % q.question

  q = Quiz.Question()
  q.add_text("The answer is c... its always c.")
  text = q.emit(q_emit)
  assert text == "Question: 'The answer is c... its always c.'\nThe answer is irrelevent"

def test_quiz_passthroughs():
  q = Quiz()
  q.add_question()
  q.add_text( 'is question' )
  q.add_text( 'This', prepend=True )
  q.add_text( 'one.' )

  assert q.question.emit() == 'This is question one.'

  q.add_instruction('please.')
  q.add_instruction('Follow these instructions', prepend=True)

  assert q.question.emit() == 'This is question one. Follow these instructions please.'

  a = MultipleChoiceAnswer()
  a.add_choices('''
  one
  *two
  three
  ''')

  q.add_answer( a )

  assert q.question.emit('bb') == 'MC\tThis is question one. Follow these instructions please.\tone\tincorrect\ttwo\tcorrect\tthree\tincorrect'

  q.set_text( 'Different' )
  q.add_text( 'question, same answer.' )

  assert q.question.emit('bb') == 'MC\tDifferent question, same answer. Follow these instructions please.\tone\tincorrect\ttwo\tcorrect\tthree\tincorrect'

  q.set_instruction( 'No special instructions.' )

  assert q.question.emit('bb') == 'MC\tDifferent question, same answer. No special instructions.\tone\tincorrect\ttwo\tcorrect\tthree\tincorrect'

  a = MultipleChoiceAnswer()
  a.add_choices('''
  one
  *two
  *three
  ''')

  q.set_answer( a )

  assert q.question.emit('bb') == 'MA\tDifferent question, same answer. No special instructions.\tone\tincorrect\ttwo\tcorrect\tthree\tcorrect'

def test_quiz_bb_emitter():
  q = Quiz()

  q.add_question()
  q.add_text('one')
  a = MultipleChoiceAnswer()
  a.add_choices('''
  a
  *b
  ''')
  q.add_answer(a)

  q.add_question()
  q.add_text('two')
  a = MultipleChoiceAnswer()
  a.add_choices('''
  *c
  d
  ''')
  q.add_answer(a)

  q.add_question()
  q.add_text('three')
  a = MultipleChoiceAnswer()
  a.add_choices('''
  *e
  *f
  ''')
  q.add_answer(a)


  text = q.emit('bb')

  assert text == 'MC\tone\ta\tincorrect\tb\tcorrect\nMC\ttwo\tc\tcorrect\td\tincorrect\nMA\tthree\te\tcorrect\tf\tcorrect'


  q.order = [2,0,1]

  text = q.emit('bb')

  assert text == 'MA\tthree\te\tcorrect\tf\tcorrect\nMC\tone\ta\tincorrect\tb\tcorrect\nMC\ttwo\tc\tcorrect\td\tincorrect'


def test_quiz_custom_emitter():
  def quiz_emit(quiz):
    tokens = []
    for q in quiz.questions:
      tokens.append( q.question )
    return '\n'.join(tokens)

  q = Quiz()

  q.add_question()
  q.add_text('one')
  a = MultipleChoiceAnswer()
  a.add_choices('''
  a
  *b
  ''')
  q.add_answer(a)

  q.add_question()
  q.add_text('two')
  a = MultipleChoiceAnswer()
  a.add_choices('''
  *c
  d
  ''')
  q.add_answer(a)

  q.add_question()
  q.add_text('three')
  a = MultipleChoiceAnswer()
  a.add_choices('''
  *e
  *f
  ''')
  q.add_answer(a)


  text = q.emit(quiz_emit)

  assert text == 'one\ntwo\nthree'
