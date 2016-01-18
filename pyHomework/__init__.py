import sys

try:
  import sympy
  from .sympy import *
  from .sympy.Equations import *
except Exception as e:
  print "sympy failed to import. sympy support disabled."
  print "Error Raised:"
  print e
 
try:
  from .numpy.quantity_calcs import *
except Exception as e:
  print "numpy failed to import. numpy support disabled."
  print "Error Raised:"
  print e

from .Constants import *
from .HomeworkAssignment import *

