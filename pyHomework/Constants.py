import math
from pyErrorProp.util import sigfig_round

class ConstantsCollection:

  def __init__(self, UR, sigfigs=None ):
    self.UnitRegistry = UR
    Q = UR.Quantity

    def make( value, unit ):
      return sigfig_round( Q( value, unit ), n = sigfigs )

    self.Pi                    = make(math.pi,              'dimensionless')
    self.AvagadrosNumber       = make(6.0221409e+23,        '')
    self.AvagadrosConstant     = make(self.AvagadrosNumber.magnitude, '1/mol')

    self.GravitationalAcceleration = make(9.80,             'm s^-2')
    self.SpeedOfLight          = make(299792458,            'm/s')
    self.GravitationalConstant = make(6.6738e-11,           'm^3 kg^-1 s^-2')
    self.ElementaryCharge      = make(1.602e-19,            'coulomb')
    self.CoulombsConstant      = make(8.9875517873681764e9, 'N m^2 / C^2')
    self.VacuumPermittivity    = make(8.85418782e-12,       'F/m')
    self.VacuumPermeability    = make(4*math.pi*1e-7,       'N/A^2')
    self.PlancksConstant       = make(6.62607004e-34, 'm^2 kg / s')
    self.BoltzmannConstant     = make(1.38064852e-23, 'm^2 kg / s^2 / degK')
    self.UniversalGasConstant  = make(8.3144598,      'J/mol/degK')

    self.Distances = {}
    self.Distances['moon'] = make( 238900, 'mile' )
    self.Distances['sun']  = make( 92.96e6, 'mile' )

    self.Masses = {}
    self.Masses['sun']      = make(1.989e30,       'kg')
    self.Masses['earth']    = make(5.972e24,       'kg')
    self.Masses['moon']     = make(7.34767309e22,  'kg')
    self.Masses['electron'] = make(9.10938356e-31, 'kg')
    self.Masses['proton']   = make(1.6726219e-27,  'kg')

    self.MolarMasses = {}
    self.MolarMasses['nitrogen'] = make(14.0067,'g/mol')
    self.MolarMasses['oxygen']   = make(15.9994,'g/mol')

    self.Charges = {}
    self.Charges['electron'] = -self.ElementaryCharge
    self.Charges['proton']   =  self.ElementaryCharge

    self.Radii = {}
    self.Radii['sun']   = make(432474, 'mile' )
    self.Radii['earth'] = make(3959,   'mile' )

    # these values are taken from the OpenStax College Physics textbook
    self.RefractiveIndexes = { 'water'       : { 'nominal' : make(1.333, '' ) }
                             , 'crown glass' : { 'nominal' : make(1.52 , '' )
                                               , 'red'     : make(1.512, '')
                                               , 'orange'  : make(1.514, '')
                                               , 'yellow'  : make(1.518, '')
                                               , 'green'   : make(1.519, '')
                                               , 'blue'    : make(1.524, '')
                                               , 'violet'  : make(1.530, '')
                                               }
                             , 'flint glass' : { 'nominal' : make(1.66,    '' ) }
                             , 'air'         : { 'nominal' : make(1.00293, '' ) }
                             , 'glycerine'   : { 'nominal' : make(1.473,   '' ) }
                             , 'ice'         : { 'nominal' : make(1.309,   '' ) }
                             }

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

    self.Densities = {}
    self.Densities['water'] = make(1,       'g/cm^3')

    self.LatentHeats = {}
    self.LatentHeats['ice2water'] = make(333, 'J/g')

    self.SpecificHeats = {}
    self.SpecificHeats['water'] = make(1, 'cal/g/K')

    # Shorthand Names
    for k,v in self.Masses.items():
      setattr(self, "Mass%s"%k.capitalize(), v)

    for k,v in self.Radii.items():
      setattr(self, "Radius%s"%k.capitalize(), v)

