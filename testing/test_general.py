from pyHomework import Constants
from pyHomework.sympy import Equations

import sympy as sy

def Close( a, b, tol = 0.01 ):
    if isinstance(a,int):
        a = float(a)
    if isinstance(b,int):
        b = float(b)
    return (a - b)**2 / (a**2 + b**2) < 4*tol*tol

def test_constants():
  import pint
  units = pint.UnitRegistry()
  consts = Constants.ConstantsCollection( units )

  assert '3.0e+08 m / s'    == '{:.1e~}'.format( consts.SpeedOfLight.to('m/s') )
  assert '3.00e+08 m / s'   == '{:.2e~}'.format( consts.SpeedOfLight.to('m/s') )
  assert '2.998e+08 m / s'  == '{:.3e~}'.format( consts.SpeedOfLight.to('m/s') )
  assert '2.9979e+08 m / s' == '{:.4e~}'.format( consts.SpeedOfLight.to('m/s') )

  assert '6.7e-11 m ** 3 / kg / s ** 2'    == '{:.1e~}'.format( consts.GravitationalConstant.to('m^3 kg^-1 s^-2') )
  assert '6.67e-11 m ** 3 / kg / s ** 2'   == '{:.2e~}'.format( consts.GravitationalConstant.to('m^3 kg^-1 s^-2') )
  assert '6.674e-11 m ** 3 / kg / s ** 2'  == '{:.3e~}'.format( consts.GravitationalConstant.to('m^3 kg^-1 s^-2') )
  assert '6.6738e-11 m ** 3 / kg / s ** 2' == '{:.4e~}'.format( consts.GravitationalConstant.to('m^3 kg^-1 s^-2') )



  consts = Constants.ConstantsCollection( units, sigfigs=2 )

  assert '3.0e+08 m / s'    == '{:.1e~}'.format( consts.SpeedOfLight.to('m/s') )
  assert '3.00e+08 m / s'   == '{:.2e~}'.format( consts.SpeedOfLight.to('m/s') )
  assert '3.000e+08 m / s'  == '{:.3e~}'.format( consts.SpeedOfLight.to('m/s') )
  assert '3.0000e+08 m / s' == '{:.4e~}'.format( consts.SpeedOfLight.to('m/s') )

  assert '6.7e-11 m ** 3 / kg / s ** 2'    == '{:.1e~}'.format( consts.GravitationalConstant.to('m^3 kg^-1 s^-2') )
  assert '6.70e-11 m ** 3 / kg / s ** 2'   == '{:.2e~}'.format( consts.GravitationalConstant.to('m^3 kg^-1 s^-2') )
  assert '6.700e-11 m ** 3 / kg / s ** 2'  == '{:.3e~}'.format( consts.GravitationalConstant.to('m^3 kg^-1 s^-2') )
  assert '6.7000e-11 m ** 3 / kg / s ** 2' == '{:.4e~}'.format( consts.GravitationalConstant.to('m^3 kg^-1 s^-2') )


def test_quantity_calcs():
  pass

def test_equations():
  eqs = Equations.EquationsCollection()

  assert 'K == m*v**2/2' == str(eqs.KineticEnergy)
  assert 'U == g_*h*m'    == str(eqs.GravitationalPotentialEnergy)


def test_sympy_solve():
  import pint
  units = pint.UnitRegistry()
  Q = units.Quantity
  e = Equations.EquationsCollection()
  e.c = Constants.ConstantsCollection( units )
  s = e.s
  
  K = e.eval( e.KineticEnergy, s.K, { s.m : Q(2.,'kg')
                                    , s.v : Q(3.,'cm/s') } )

  assert Close( 0.5*2.*3.*3./100./100., K.to('kg m^2 / s^2').magnitude )

