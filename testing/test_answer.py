
import pytest
import yaml

from pyHomework.Quiz import Quiz
from pyHomework.Answer import *
from pyHomework.Emitter import *
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
  assert a.units == 'foot'

  a.quantity = 1.2
  assert a.units == ''

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
  bb = a.emit(BbEmitter)
  assert bb == '1.23E+00\t1.23E-02'

  q = Q_(1.3579,'m/s^2')
  a = NumericalAnswer(q)
  bb = a.emit(BbEmitter)
  assert bb == '1.36E+00\t1.36E-02'
  a.sigfigs = 4
  bb = a.emit(BbEmitter)
  assert bb == '1.358E+00\t1.358E-02'


  q = UQ_(1.3579, 0.89, 'm/s^2')
  a = NumericalAnswer(q)
  bb = a.emit(BbEmitter)
  assert bb == '1.36E+00\t8.90E-01'

def test_emitter_exceptions():
  q = 1.23456789
  a = NumericalAnswer(q)
  with pytest.raises(RuntimeError) as e:
    a.emit('undefined')
  assert str(e.value) == "Unknown emitter type 'undefined' given."


  a = MultipleChoiceAnswer()
  with pytest.raises(RuntimeError) as e:
    a.emit('undefined')
  assert str(e.value) == "Unknown emitter type 'undefined' given."

def test_custom_emitters():
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

def test_factory():
  spec = { 'value' : 1.23456789 }
  a = make_answer( spec )
  assert a.quantity == '1.23E+00'
  assert a.value    == '1.23E+00'

  a = make_answer({ 'value' : '1.2345 m' })
  assert a.quantity == '1.23E+00 meter'
  assert a.value    == '1.23E+00'


  a = make_answer( {'choices' : [ 'one', '*two', 'three' ] } )
  assert a.emit() == 'two'


  a = make_answer( {'choices' : [ 'one', '*two', '*three' ] } )
  assert a.emit() == 'two, three'

  spec = { 'ordered' : ['one', 'two', 'three'] }
  a = make_answer( spec )
  assert a.emit() == 'one -> two -> three'

def test_multiple_choice_answer():
  a = MultipleChoiceAnswer()
  a.add_choice('one')
  a.add_choice('*two')
  a.add_choice('three')

  assert a.emit() == 'two'

  a.add_choice('*four')

  assert a.emit() == 'two, four'

def test_multiple_choice_answer_bb_emitter():
  a = MultipleChoiceAnswer()
  a.add_choice('one')
  a.add_choice('*two')
  a.add_choice('three')
  a.add_choice('*four')

  bb = a.emit(BbEmitter)

  assert bb == 'one\tincorrect\ttwo\tcorrect\tthree\tincorrect\tfour\tcorrect'

def test_written_answer():
  a = ShortAnswer('''Since A > B and B > C, A must also be > C.''')

  bb = a.emit(BbEmitter)
  assert bb == 'Since A > B and B > C, A must also be > C.'

def test_latex_answer():
  pass

def test_numerical_answer_loading():
  a = NumericalAnswer()


  a.load( { 'value' : 1.23456789 } )
  assert a.quantity == '1.23E+00'
  assert a.value    == '1.23E+00'

  a.load({ 'value' : 13.579 })
  assert a.quantity == '1.36E+01'
  assert a.value    == '1.36E+01'

  a.load({ 'value' : '1.2345 m' })
  assert a.quantity == '1.23E+00 meter'
  assert a.value    == '1.23E+00'

  a.load({ 'value' : '12.345 m/s' })
  assert a.quantity == '1.23E+01 meter / second'
  assert a.value    == '1.23E+01'

  a.load({ 'value' : '1.3579 m/s^2' })
  assert a.quantity == '1.36E+00 meter / second ** 2'
  assert a.value    == '1.36E+00'
  a.sigfigs = 4
  assert a.quantity == '1.358E+00 meter / second ** 2'
  assert a.value    == '1.358E+00'

  a.sigfigs = 3

  a.load({ 'value' : 1.23456789
         , 'uncertainty' : '1%'})
  assert a.uncertainty == '1.23E-02'

  a.load({ 'value' : 1.23456789
         , 'uncertainty' : '10%'})
  assert a.uncertainty == '1.23E-01'

  a.load({ 'value' : 1.23456789
         , 'uncertainty' : 0.5})
  assert a.uncertainty == '5.00E-01'

  a.load({ 'value' : Q_(2,'m/s')
         , 'uncertainty' : Q_(0.5,'m/s') })
  assert a.uncertainty == '5.00E-01'

  a.load({ 'value' : Q_(2,'m/s')
         , 'uncertainty' : Q_(0.5,'mm/s') })
  assert a.uncertainty == '5.00E-04'

  a.load({ 'value' : Q_(2,'km/s')
         , 'uncertainty' : Q_(0.5,'m/s') })
  assert a.uncertainty == '5.00E-04'

  # a.load({ 'value' :  '(2 +- 0.01) m/s' } )
  # assert a.uncertainty == '1.00E-02'

def test_multiple_choice_answer_loading():
  a = MultipleChoiceAnswer()

  a.load( {'choices' : [ 'one', '*two', 'three' ] } )

  assert a.emit() == 'two'

  a.load( {'choices' : [ 'one', '*two', 'three', '*four' ] } )

  assert a.emit() == 'two, four'

def test_latex_emitter():
  a = MultipleChoiceAnswer()
  a.add_choices('''
  *a1
  a2
  a3
  ''')

  text = a.emit(LatexEmitter)
  assert text == '@ a1\n@ a2\n@ a3'

  a = MultipleChoiceAnswer()
  a.add_choices('''
  *a1
  *a2
  a3
  ''')

  text = a.emit(LatexEmitter)
  assert text == '@ a1\n@ a2\n@ a3'

  q = 1.23456789
  a = NumericalAnswer(q)

  text = a.emit(LatexEmitter)

  assert text == ''

def test_latex_labels_emitter():
  a = MultipleChoiceAnswer()
  a.add_choices('''
  *a1
  a2
  a3
  ''')
  lbls = [ id(c) for (cc,c) in a.choices ]

  text = a.emit(LatexEmitter(labels=True))
  assert text == '@ \\label{%s}a1\n@ \\label{%s}a2\n@ \\label{%s}a3' % tuple(lbls)

  a.add_choices('''
  *a1
  *a2
  a3
  ''')

  lbls += [ id(c) for c in a._choices[3:] ]

  text = a.emit(LatexEmitter(labels=True))
  assert text == '@ \\label{%s}a1\n@ \\label{%s}a2\n@ \\label{%s}a3\n@ \\label{%s}a1\n@ \\label{%s}a2\n@ \\label{%s}a3' % tuple(lbls)

def test_latex_compactenum_emitter():
  a = MultipleChoiceAnswer()
  a.add_choices('''
  *a1
  a2
  a3
  ''')

  text = a.emit(LatexEmitter('compactenum'))
  assert text == '\\begin{compactenum}\n\\item a1\n\\item a2\n\\item a3\n\\end{compactenum}'

  a = MultipleChoiceAnswer()
  a.add_choices('''
  *a1
  *a2
  a3
  ''')

  text = a.emit(LatexEmitter('compactenum'))
  assert text == '\\begin{compactenum}\n\\item a1\n\\item a2\n\\item a3\n\\end{compactenum}'

  q = 1.23456789
  a = NumericalAnswer(q)

  text = a.emit(LatexEmitter)

  assert text == ''
