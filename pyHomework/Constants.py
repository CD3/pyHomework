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

    self.GravitationalAcceleration = make(9.80,             'm s^-2')
    self.SpeedOfLight          = make(299792458,            'm/s')
    self.GravitationalConstant = make(6.6738e-11,           'm^3 kg^-1 s^-2')
    self.ElementaryCharge      = make(1.602e-19,            'coulomb')
    self.CoulombsConstant      = make(8.9875517873681764e9, 'N m^2 / C^2')
    self.VacuumPermittivity    = make(8.85418782e-12,       'F/m')
    self.VacuumPermeability    = make(4*math.pi*1e-7,       'N/A^2')
    self.PlancksConstant       = make(6.62607004e-34, 'm^2 kg / s')
    self.BoltzmannConstant     = make(1.38064852e-23, 'm^2 kg / s^2 / K')

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

    self.DielectricConstants = {} # these values are taken from the OpenStax College Physics textbook
    self.DielectricConstants['vacuum']             = make( 1.00000 , 'dimensionless')
    self.DielectricConstants['air']                = make( 1.00059 , 'dimensionless')
    self.DielectricConstants['bakelite']           = make( 4.9     , 'dimensionless')
    self.DielectricConstants['fused quartz']       = make( 3.78    , 'dimensionless')
    self.DielectricConstants['neoprene rubber']    = make( 6.7     , 'dimensionless')
    self.DielectricConstants['nylon']              = make( 3.4     , 'dimensionless')
    self.DielectricConstants['paper']              = make( 3.7     , 'dimensionless')
    self.DielectricConstants['polystyrene']        = make( 2.56    , 'dimensionless')
    self.DielectricConstants['pyrex glass']        = make( 5.6     , 'dimensionless')
    self.DielectricConstants['silicon oil']        = make( 2.5     , 'dimensionless')
    self.DielectricConstants['strontium titanate'] = make( 233     , 'dimensionless')
    self.DielectricConstants['teflon']             = make( 2.1     , 'dimensionless')
    self.DielectricConstants['water']              = make( 80      , 'dimensionless')

    self.DielectricStrengths = {} # these values are taken from the OpenStax College Physics textbook
    self.DielectricStrengths['air']                = make( 3e6  , 'V/m')
    self.DielectricStrengths['bakelite']           = make(24e6  , 'V/m')
    self.DielectricStrengths['fused quartz']       = make( 8e6  , 'V/m')
    self.DielectricStrengths['neoprene rubber']    = make(12e6  , 'V/m')
    self.DielectricStrengths['nylon']              = make(14e6  , 'V/m')
    self.DielectricStrengths['paper']              = make(16e6  , 'V/m')
    self.DielectricStrengths['polystyrene']        = make(24e6  , 'V/m')
    self.DielectricStrengths['pyrex glass']        = make(14e6  , 'V/m')
    self.DielectricStrengths['silicon oil']        = make(15e6  , 'V/m')
    self.DielectricStrengths['strontium titanate'] = make( 8e6  , 'V/m')
    self.DielectricStrengths['teflon']             = make(60e6  , 'V/m')

    self.Resistivities = {}
    self.Resistivities['silver']   = make( 1.59E-8, 'ohm m')
    self.Resistivities['copper']   = make( 1.72E-8, 'ohm m')
    self.Resistivities['gold']     = make( 2.44E-8, 'ohm m')
    self.Resistivities['aluminum'] = make( 2.65E-8, 'ohm m')
    self.Resistivities['tungsten'] = make( 5.60E-8, 'ohm m')
    self.Resistivities['nichrome'] = make(  100E-8, 'ohm m')

    self.ResistivityCoefficients = {}
    self.ResistivityCoefficients['silver']   = make( 3.8E-3, '1/delta_degC')
    self.ResistivityCoefficients['copper']   = make( 3.9E-3, '1/delta_degC')
    self.ResistivityCoefficients['gold']     = make( 3.4E-3, '1/delta_degC')
    self.ResistivityCoefficients['aluminum'] = make( 3.9E-3, '1/delta_degC')
    self.ResistivityCoefficients['tungsten'] = make( 4.5E-3, '1/delta_degC')
    self.ResistivityCoefficients['nichrome'] = make( 0.4E-3, '1/delta_degC')

    # some shorthands for common constants
    self.MassOfSun             = self.Masses['sun']
    self.MassOfEarth           = self.Masses['earth']
    self.MassOfMoon            = self.Masses['moon']
    self.MassOfElectron        = self.Masses['electron']
    self.MassOfProton          = self.Masses['proton']

    self.RadiusOfSun           = self.Radii['sun']
    self.RadiusOfEarth         = self.Radii['earth']

