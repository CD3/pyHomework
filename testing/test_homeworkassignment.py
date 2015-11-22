from pyHomework import HomeworkAssignment as HA

def Close( a, b, tol = 0.001 ):
    if isinstance(a,int):
        a = float(a)
    if isinstance(b,int):
        b = float(b)
    return (a - b)**2 / (a**2 + b**2) < 4*tol*tol

def test_quiz():
  ass = HA.HomeworkAssignment()


  ass.add_question()
  ass.add_text("Question #1")
  
  ass.add_part()
  ass.add_text("Question #1, Part a")

  ass.add_part()
  ass.add_text("Question #1, Part a")


  ass.add_question()
  ass.add_text("Question #2")
  
  ass.add_part()
  ass.add_text("Question #2, Part a")

  ass.add_part()
  ass.add_text("Question #2, Part a")


  ass.add_question()
  ass.add_text("Question #3")

  ass.add_quiz_question()
  ass.quiz_add_text("What is the answer?")


def test_numerical_answer():
  import pint
  units = pint.UnitRegistry()
  Q_ = units.Quantity
  M_ = units.Measurement

  Answer = Q_(1.2345,'m/s')
  a = HA.NumericalAnswer(Answer)
  d = a.dict()

  assert d['value'] == '1.23E+00'
  assert d['uncertainty'] == '1%'
  assert d['unit'] == 'meter / second'


  Answer = M_(1.2345,0.034,'m/s')
  a = HA.NumericalAnswer(Answer)
  d = a.dict()

  assert d['value'] == '1.234E+00'
  assert d['uncertainty'] == '0.034E+00'
  assert d['unit'] == 'meter / second'


  Answer = Q_(123.45,'m/s')
  a = HA.NumericalAnswer(Answer)
  d = a.dict()

  assert d['value'] == '1.23E+02'
  assert d['uncertainty'] == '1%'
  assert d['unit'] == 'meter / second'


  Answer = M_(123.45,3.4,'m/s')
  a = HA.NumericalAnswer(Answer)
  d = a.dict()

  assert d['value'] == '1.234E+02'
  assert d['uncertainty'] == '0.034E+02'
  assert d['unit'] == 'meter / second'


  Answer = Q_(0.00012345,'m/s')
  a = HA.NumericalAnswer(Answer)
  d = a.dict()

  assert d['value'] == '1.23E-04'
  assert d['uncertainty'] == '1%'
  assert d['unit'] == 'meter / second'


  Answer = M_(0.00012345,0.0000034,'m/s')
  a = HA.NumericalAnswer(Answer)
  d = a.dict()

  assert d['value'] == '1.234E-04'
  assert d['uncertainty'] == '0.034E-04'
  assert d['unit'] == 'meter / second'

