
import pytest
import yaml

from pyHomework.Quiz import Quiz
from pyHomework.Answer import *
from pyHomework.Emitter import *

from pyErrorProp import *

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

  assert q.question.emit(BbEmitter) == 'MC\tThis is question one. Follow these instructions please.\tone\tincorrect\ttwo\tcorrect\tthree\tincorrect'

  q.set_text( 'Different' )
  q.add_text( 'question, same answer.' )

  assert q.question.emit(BbEmitter) == 'MC\tDifferent question, same answer. Follow these instructions please.\tone\tincorrect\ttwo\tcorrect\tthree\tincorrect'

  q.set_instruction( 'No special instructions.' )

  assert q.question.emit(BbEmitter) == 'MC\tDifferent question, same answer. No special instructions.\tone\tincorrect\ttwo\tcorrect\tthree\tincorrect'

  a = MultipleChoiceAnswer()
  a.add_choices('''
  one
  *two
  *three
  ''')

  q.set_answer( a )

  assert q.question.emit(BbEmitter) == 'MA\tDifferent question, same answer. No special instructions.\tone\tincorrect\ttwo\tcorrect\tthree\tcorrect'

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


  text = q.emit(BbEmitter)

  assert text == 'MC\tone\ta\tincorrect\tb\tcorrect\nMC\ttwo\tc\tcorrect\td\tincorrect\nMA\tthree\te\tcorrect\tf\tcorrect'


  q.order = [2,0,1]

  text = q.emit(BbEmitter)

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

def test_yaml_to_bb_quiz():
  quiztext = '''
configuration:
  randomize:
    questions: False
    answers: False
  special_chars:
    correct_answer : '*'
  remote:
    web_root: 'http://scatcat.fhsu.edu/~cdclark/'
    copy_root: 'ssh://cdclark@scatcat.fhsu.edu/~/public_html'
    image_dir : 'images'

questions:
  -
    text: "Q1"
    answer:
      choices:
      - '*a1'
      - 'a2'
      - 'a3'

  -
    text: "Q2"
    answer:
      choices:
      - '*a1'
      - 'a2'
      - '*a3'

  -
    text: "Q3"
    answer:
      value : 7
  -
    text: "Q4"
    answer:
      value : 7
      uncertainty: 20%
  -
    text: "Q5"
    answer:
      logical: True
  '''
  quizdict = yaml.load( quiztext )

  q = Quiz()
  q.load( quizdict )

  bbquiz = q.emit(BbEmitter)
  assert bbquiz == 'MC\tQ1\ta1\tcorrect\ta2\tincorrect\ta3\tincorrect\nMA\tQ2\ta1\tcorrect\ta2\tincorrect\ta3\tcorrect\nNUM\tQ3\t7.00E+00\t7.00E-02\nNUM\tQ4\t7.00E+00\t1.40E+00\nTF\tQ5\ttrue'
