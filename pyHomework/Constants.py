import math
from pyErrorProp import sigfig_round

class ConstantsCollection:

  def __init__(self, UR, sigfigs=None ):
    self.UnitRegistry = UR
    Q = UR.Quantity

    def make( value, unit ):
      return sigfig_round( Q( value, unit ), n = sigfigs )

    self.Pi                    = make(math.pi,              'dimensionless')

    self.SpeedOfLight          = make(299792458,            'm/s')
    self.GravitationalConstant = make(6.6738e-11,           'm^3 kg^-1 s^-2')
    self.MassOfSun             = make(1.989e30,             'kg')
    self.RadiusOfSun           = make(696300,               'km' )
    self.MassOfEarth           = make(5.972e24,             'kg')
    self.RadiusOfEarth         = make(3959,                 'mile' )
    self.MassOfMoon            = make(7.34767309e22,        'kg')

    self.Avagadros             = make(6.022e23,             '1/mol')
    self.GravityConstant       = make(6.67,                 'N m^2 / kg^2')
    self.ElementaryCharge      = make(1.602e-19,            'coulomb')
    self.MassOfElectron        = make(9.109e-31,            'kg')
    self.MassOfProton          = make(1.673e-27,            'kg')
    self.CoulombsConstant      = make(8.9875517873681764e9, 'N m^2 / C^2')
    self.VacuumPermittivity    = make(8.85418782,           'F/m')

    self.VacuumPermeability    = make(4*math.pi*1e-7,       'N/A^2')

