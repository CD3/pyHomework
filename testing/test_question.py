
import pytest
import yaml
import utils

from pyHomework.Question import *
from pyHomework.Answer import *
from pyHomework.Emitter import *
from pyErrorProp import *

def test_add_text():
  q = Question()

  q.add_text( "Second sentence." )
  q.add_text( "Third")
  q.add_text( "sentence." )
  q.add_text( "First sentence.", prepend=True )
  q.add_text( "{x}" )
  q.add_text( "{y}" )
  q.format_text( y = "Fifth sentence." )
  q.format_text( x = "Fourth sentence." )

  assert q.text_str == "First sentence. Second sentence. Third sentence. Fourth sentence. Fifth sentence."

def test_add_instruction():
  q = Question()
  q.add_instruction("text.")
  q.add_instruction("Instruction", prepend=True)

  assert q.instructions_str == "Instruction text."

def test_add_text_and_instruction():
  q = Question()
  q.add_text("Question text.")
  q.add_instruction("Instruction text.")
  q.add_pre_instruction("Pre, Instruction text.")

  assert q.question_str == "Pre, Instruction text. Question text. Instruction text."

def test_set_text():
  q = Question()

  q.add_text( "one" )
  q.add_text( "two")
  q.add_text( "three" )

  q.set_text( "four" )

  assert q.question_str == "four"

def test_set_instruction():
  q = Question()

  q.add_instruction( "one" )
  q.add_instruction( "two")
  q.add_instruction( "three" )

  q.set_instruction( "four" )

  assert q.question_str == "four"

@pytest.mark.skip()
def test_question_with_numerical_answer():
  q = Question()

  l = Q_(1.5,'m')
  w = Q_(2.5,'m')
  # print l*w
  q.add_text("What is the area of a {l} x {w} square?")
  q.format_text( l=l, w=w, formatter='format' )
  q.auto_answer_instructions = False
  q.set_answer( NumericalAnswer( l*w ) )

  text = q.emit(BbEmitter)
  assert text == 'NUM\tWhat is the area of a 1.5 meter x 2.5 meter square?\t3.75E+00\t3.75E-02'

@pytest.mark.skip()
def test_question_with_mc_answer():
  q = Question()

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

@pytest.mark.skip()
def test_mc_ordering():
  q = Question()

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

@pytest.mark.skip()
def test_question_with_ma_answer():
  q = Question()

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
  q = Question()
  q.add_text("The answer is c... its always c.")
  with pytest.raises(RuntimeError) as e:
    q.emit('undefined')
  assert str(e.value) == "Unknown emitter type 'undefined' given."

def test_emitter_exceptions():
  def q_emit(q):
    return "Question: '%s'\nThe answer is irrelevent" % q.question_str

  q = Question()
  q.add_text("The answer is c... its always c.")
  text = q.emit(q_emit)
  assert text == "Question: 'The answer is c... its always c.'\nThe answer is irrelevent"

@pytest.mark.skip()
def test_latex_emitter():
  q = Question()

  q.add_text("Q1")
  a = MultipleChoiceAnswer()
  a.add_choices('''
  *a1
  a2
  a3
  ''')
  q.set_answer( a )

  text = q.emit(LatexEmitter)
  assert text == '@ Q1\n@@ a1\n@@ a2\n@@ a3'

  q.add_answer( a )

  text = q.emit(LatexEmitter)
  assert text == '@ Q1\n@@ a1\n@@ a2\n@@ a3\n@@ a1\n@@ a2\n@@ a3'





  q = Question()
  qa = Question()

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
  assert text == '@ Q1\n@@ a1\n@@ a2\n@@ a3\n@@ Q1a\n@@@ aa1\n@@@ aa2\n@@@ aa3'

  text = q.last_part.emit(LatexEmitter)
  assert text == '@ Q1a\n@@ aa1\n@@ aa2\n@@ aa3'

@pytest.mark.skip()
def test_latex_labels_emitter():
  q = Question()

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
  assert text == '@ \\label{%s}Q1\n@@ \\label{%s}a1\n@@ \\label{%s}a2\n@@ \\label{%s}a3' % tuple(lbls)

  a = MultipleChoiceAnswer()
  a.add_choices('''
  *a1
  a2
  a3
  ''')
  q.set_answer( a )

  text = q.emit(LatexEmitter(labels=True))
  assert text != '@ \\label{%s}Q1\n@@ \\label{%s}a1\n@@ \\label{%s}a2\n@@ \\label{%s}a3' % tuple(lbls)

@pytest.mark.skip()
def test_latex_compactenum_emitter():
  q = Question()

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





  q = Question()
  qa = Question()

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

def test_with_interface():

  q = Question()

  q.add_text("Q1")

  with q._add_part() as p:
    p.add_text("Q1a")

    with p._add_part() as pp:
      pp.add_text("Q1aa")

      with pp._add_answer( MultipleChoiceAnswer() ) as a:
        a.add_choices(r'''
          *a
           b
           c
        ''')


  text = q.emit(LatexEmitter)
  assert text == '@ Q1\n@@ Q1a\n@@@ Q1aa\n@@@@ a\n@@@@ b\n@@@@ c'

  text = q.last_part.emit(LatexEmitter)
  assert text == '@ Q1a\n@@ Q1aa\n@@@ a\n@@@ b\n@@@ c'

  text = q.last_part.last_part.emit(LatexEmitter)
  assert text == '@ Q1aa\n@@ a\n@@ b\n@@ c'


  with q._set_part() as p:
    p.add_text("q1a")

    with p._add_part() as pp:
      pp.add_text("q1aa")


  text = q.emit(LatexEmitter)
  assert text == '@ Q1\n@@ q1a\n@@@ q1aa'

  text = q.last_part.emit(LatexEmitter)
  assert text == '@ q1a\n@@ q1aa'

  text = q.last_part.last_part.emit(LatexEmitter)
  assert text == '@ q1aa'



@pytest.mark.skip()
def test_with_interface_replace():
  # swap  '_' prefixed versions with non-prefixed versions
  Question_add_part = Question.add_part
  Question_set_part = Question.set_part
  Question.add_part = Question._add_part
  Question.set_part = Question._set_part

  Question_add_answer = Question.add_answer
  Question_set_answer = Question.set_answer
  Question.add_answer = Question._add_answer
  Question.set_answer = Question._set_answer

  q = Question()

  q.add_text("Q1")

  with q.add_part() as p:
    p.add_text("Q1a")

    with p.add_part() as pp:
      pp.add_text("Q1aa")

      with pp.add_answer( MultipleChoiceAnswer() ) as a:
        a.add_choices(r'''
          *a
           b
           c
        ''')


  text = q.emit(LatexEmitter)
  assert text == '@ Q1\n@@ Q1a\n@@@ Q1aa\n@@@@ a\n@@@@ b\n@@@@ c'

  text = q.last_part.emit(LatexEmitter)
  assert text == '@ Q1a\n@@ Q1aa\n@@@ a\n@@@ b\n@@@ c'

  text = q.last_part.last_part.emit(LatexEmitter)
  assert text == '@ Q1aa\n@@ a\n@@ b\n@@ c'

  Question.add_part = Question_add_part
  Question.set_part = Question_set_part
  Question.add_answer = Question_add_answer
  Question.set_answer = Question_set_answer

@pytest.mark.skip()
def test_with_interface_restore():
  # check that we can still use non-contextmanager interface
  q = Question()
  q.add_text("Q1")
  q.add_part()
  q.last_part.add_text("Q1a")
  q.last_part.add_part()
  q.last_part.last_part.add_text("Q1aa")

  text = q.emit(LatexEmitter)
  assert text == '@ Q1\n@@ Q1a\n@@@ Q1aa'

  text = q.last_part.emit(LatexEmitter)
  assert text == '@ Q1a\n@@ Q1aa'

  text = q.last_part.last_part.emit(LatexEmitter)
  assert text == '@ Q1aa'

def test_function_calling():

  def func(a,b,c):
    return a+b+c

  q = Question()

  with pytest.raises(RuntimeError) as e:
    q.call(func)

  q.a = 1
  with pytest.raises(RuntimeError) as e:
    q.call(func, b=2)

  q.a = 1
  q.b = 2
  q.c = 3

  assert q.call(func) == 6

  assert q.ecall(func).value.magnitude == 6
  assert utils.Close( q.ecall(func).error.magnitude , (3*0.01**2)**0.5 )

  assert q.ecall(func,a=4).value.magnitude == 9
  assert utils.Close( q.ecall(func).error.magnitude , (3*0.01**2)**0.5 )



  assert q.call( lambda a,b,c : 2*a + 2*b + 2*c ) == 12

  assert q.ecall( lambda a,b,c : 2*a + 2*b + 2*c ).value.magnitude == 12
  assert utils.Close( q.ecall( lambda a,b,c : 2*a + 2*b + 2*c ).error.magnitude , (3*(2*0.01)**2)**0.5 )
  
