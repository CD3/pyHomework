
import pytest
import yaml

from pyHomework.Quiz import Quiz
from pyHomework.Answer import *
from pyHomework.Emitter import *
from pyErrorProp import *

def test_add_text():
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

def test_add_instruction():
  q = Quiz.Question()
  q.add_instruction("text.")
  q.add_instruction("Instruction", prepend=True)

  assert q.instructions == "Instruction text."

def test_add_text_and_instruction():
  q = Quiz.Question()
  q.add_text("Question text.")
  q.add_instruction("Instruction text.")

  assert q.question == "Question text. Instruction text."

  q.prepend_instructions = True
  assert q.question == "Instruction text. Question text."

  q.prepend_instructions = False
  assert q.question == "Question text. Instruction text."

def test_set_text():
  q = Quiz.Question()

  q.add_text( "one" )
  q.add_text( "two")
  q.add_text( "three" )

  q.set_text( "four" )

  assert q.question == "four"

def test_set_instruction():
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

  text = q.emit(BbEmitter)

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

  text = q.emit(BbEmitter)

  assert text == 'MC\tThe answer is c... its always c.\tthis is not the answer you are looking for.\tincorrect\tnope.\tincorrect\tthis is it!\tcorrect\treally?\tincorrect'

def test_mc_ordering():
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

  text = q.emit(BbEmitter)

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

  text = q.emit(BbEmitter)

  assert text == 'MA\tThe answer is c... its always c.\tthis is not the answer you are looking for.\tincorrect\tnope.\tincorrect\tthis is it!\tcorrect\treally?\tincorrect\toh...this one too.\tcorrect'

def test_emitter_exceptions():
  q = Quiz.Question()
  q.add_text("The answer is c... its always c.")
  with pytest.raises(RuntimeError) as e:
    q.emit('undefined')
  assert str(e.value) == "Unknown emitter type 'undefined' given."

def test_emitter_exceptions():
  def q_emit(q):
    return "Question: '%s'\nThe answer is irrelevent" % q.question

  q = Quiz.Question()
  q.add_text("The answer is c... its always c.")
  text = q.emit(q_emit)
  assert text == "Question: 'The answer is c... its always c.'\nThe answer is irrelevent"

def test_latex_emitter():
  q = Quiz.Question()

  q.add_text("Q1")
  a = MultipleChoiceAnswer()
  a.add_choices('''
  *a1
  a2
  a3
  ''')
  q.set_answer( a )

  text = q.emit(LatexEmitter)
  assert text == '& Q1\n&& a1\n&& a2\n&& a3'

  q.add_answer( a )

  text = q.emit(LatexEmitter)
  assert text == '& Q1\n&& a1\n&& a2\n&& a3\n&& a1\n&& a2\n&& a3'





  q = Quiz.Question()
  qa = Quiz.Question()

  q.add_text("Q1")
  a = MultipleChoiceAnswer()
  a.add_choices('''
  *a1
  a2
  a3
  ''')
  q.set_answer( a )

  qa.add_text("Q1a")
  aa = MultipleChoiceAnswer()
  aa.add_choices('''
  aa1
  *aa2
  aa3
  ''')
  qa.set_answer( aa )

  q.add_part( qa )

  text = q.emit(LatexEmitter)

  assert text == '& Q1\n&& a1\n&& a2\n&& a3\n&& Q1a\n&&& aa1\n&&& aa2\n&&& aa3'

def test_latex_labels_emitter():
  q = Quiz.Question()

  q.add_text("Q1")
  a = MultipleChoiceAnswer()
  a.add_choices('''
  *a1
  a2
  a3
  ''')
  q.set_answer( a )
  lbls = []
  lbls.append(id(q))
  lbls += [id(c) for c in q._answers[0]._choices]

  text = q.emit(LatexEmitter(labels=True))
  assert text == '& \\label{%s}Q1\n&& \\label{%s}a1\n&& \\label{%s}a2\n&& \\label{%s}a3' % tuple(lbls)

  a = MultipleChoiceAnswer()
  a.add_choices('''
  *a1
  a2
  a3
  ''')
  q.set_answer( a )

  text = q.emit(LatexEmitter(labels=True))
  assert text != '& \\label{%s}Q1\n&& \\label{%s}a1\n&& \\label{%s}a2\n&& \\label{%s}a3' % tuple(lbls)



def test_latex_compactenum_emitter():
  q = Quiz.Question()

  q.add_text("Q1")
  a = MultipleChoiceAnswer()
  a.add_choices('''
  *a1
  a2
  a3
  ''')
  q.set_answer( a )

  text = q.emit(LatexEmitter('compactenum'))
  assert text == '\\item Q1\n\\begin{compactenum}\n\\item a1\n\\item a2\n\\item a3\n\end{compactenum}'

  q.add_answer( a )

  text = q.emit(LatexEmitter('compactenum'))
  assert text == '\\item Q1\n\\begin{compactenum}\n\\item a1\n\\item a2\n\\item a3\n\end{compactenum}\n\\begin{compactenum}\n\\item a1\n\\item a2\n\\item a3\n\end{compactenum}'





  q = Quiz.Question()
  qa = Quiz.Question()

  q.add_text("Q1")
  a = MultipleChoiceAnswer()
  a.add_choices('''
  *a1
  a2
  a3
  ''')
  q.set_answer( a )

  qa.add_text("Q1a")
  aa = MultipleChoiceAnswer()
  aa.add_choices('''
  aa1
  *aa2
  aa3
  ''')
  qa.set_answer( aa )

  q.add_part( qa )

  text = q.emit(LatexEmitter('compactenum'))
  assert text == '\\item Q1\n\\begin{compactenum}\n\\item a1\n\\item a2\n\\item a3\n\end{compactenum}\n\\begin{compactenum}\n\\item Q1a\n\\begin{compactenum}\n\\item aa1\n\\item aa2\n\\item aa3\n\\end{compactenum}\n\\end{compactenum}'





