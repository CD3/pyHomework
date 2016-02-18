#! /bin/env python
from BoilerPlate import *

# the setup function from the BoilerPlate module
# it creates the assignment, equations, and constants instances
Setup(__file__)

with ass._add_question() as q:
  q.add_text(r'''
  What force is required to make a \SI{2.0}{\kilo\gram} accelerate at \SI{5.0}{\meter\per\second\squared}?
  ''')
  Mass = Q_(2,'kg')             # Q_ is an alias for the pint Quantity class from the UnitRegistry created by the pyHomework module
  Acceleration = Q_(2,'m/s^2')

  with quiz._add_question() as qq:
    qq.add_text(r'''
    What is the force?
    ''')
  
    with qq._set_answer( NumericalAnswer ) as a:
      a.quantity = Mass * Acceleration
  


with ass._add_question() as q:
  q.add_text(r'''
  A \SI{3.0}{\kilo\gram} mass is dropped from a height of \SI{10}{\meter}.
  ''')

  Mass = Q_(3,'kg')
  Height = Q_(10,'m')

  PE = Mass*Q_(9.8,'m/s^2')*Height

  with q._add_part() as p:
    p.add_text(r'''
    What is the velocity of the mass at the moment it strikes the ground.
    ''')

    with quiz._add_question() as qq:
      qq.add_text(r'''
      What is the velocty?
      ''')
    
      with qq._set_answer( NumericalAnswer ) as a:
        a.quantity = np.sqrt( (2*PE)/Mass )
    

  with q._add_part() as p:
    p.add_text(r'''
    How much work must be done by the normal force of the ground to stop the mass?
    ''')

    with quiz._add_question() as qq:
      qq.add_text(r'''
      How much work must be done?
      ''')
    
      with qq._set_answer( NumericalAnswer ) as a:
        a.quantity = PE
    

# the build function from the BoilerPlate module
# this creates the PDF and Bb quiz file
Build()
