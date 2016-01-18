try:
  import sympy
  from .sympy import *
  from .sympy.Equations import *
except:
  print "sympy failed to import. sympy support disabled."

try:
  from .numpy.quantity_calcs import *
except:
  print "numpy failed to import. numpy support disabled."

from .Constants import *
from .HomeworkAssignment import *

