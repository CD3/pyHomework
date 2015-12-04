import math
from pyErrorProp import sigfig_round

class ConstantsCollection:

  def __init__(self, UR, sigfigs=None ):
    self.UnitRegistry = UR
    Q = UR.Quantity

    def make( value, unit ):
      return sigfig_round( Q( value, unit ), n = sigfigs )

    self.Pi                    = make(math.pi,              'dimensionless')
    self.AvagadrosNumber       = make(6.0221409e+23,        '1/mol')

    self.SpeedOfLight          = make(299792458,            'm/s')
    self.GravitationalConstant = make(6.6738e-11,           'm^3 kg^-1 s^-2')
    self.ElementaryCharge      = make(1.602e-19,            'coulomb')
    self.CoulombsConstant      = make(8.9875517873681764e9, 'N m^2 / C^2')
    self.VacuumPermittivity    = make(8.85418782,           'F/m')
    self.VacuumPermeability    = make(4*math.pi*1e-7,       'N/A^2')

    self.Masses = {}
    self.Masses['sun']      = make(1.989e30,       'kg')
    self.Masses['earth']    = make(5.972e24,       'kg')
    self.Masses['moon']     = make(7.34767309e22,  'kg')
    self.Masses['electron'] = make(9.10938356e-31, 'kg')
    self.Masses['proton']   = make(1.6726219e-27,  'kg')

    self.Radii = {}
    self.Radii['sun']   = make(432474, 'mile' )
    self.Radii['earth'] = make(3959,   'mile' )

    self.RefractiveIndexes = {}
    self.RefractiveIndexes['water'] = make(1.333, 'dimensionless' )
    self.RefractiveIndexes['glass'] = make(1.5,   'dimensionless' )
    self.RefractiveIndexes['air']   = make(1.003, 'dimensionless' )

    # some shorthands for common constants
    self.MassOfSun             = self.Masses['sun']
    self.MassOfEarth           = self.Masses['earth']
    self.MassOfMoon            = self.Masses['moon']
    self.MassOfElectron        = self.Masses['electron']
    self.MassOfProton          = self.Masses['proton']

    self.RadiusOfSun           = self.Radii['sun']
    self.RadiusOfEarth         = self.Radii['earth']


