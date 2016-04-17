import pytest
import pint
units = pint.UnitRegistry()
Q_ = units.Quantity
UQ_ = units.Measurement

from pyHomework.Utils import *

def test_text_formatting():

  context = { 'A' : Q_(1,'m'), 'B' : Q_(2,'m/s') }

  text = r'''This is a simple string.'''
  assert text == format_text( text, formatter='format' )

  text = r'''This is a simple string.'''
  assert text == format_text( text, formatter='format', **context )

  text = r'''A = {A}.'''
  assert r"A = 1 meter." == format_text( text, formatter='format', **context )

  text = r'''A = {A}. B = {B:.2f}.'''
  assert r"A = 1 meter. B = 2.00 meter / second." == format_text( text, formatter='format', **context )

  text = r'''A = {A}. B = {B:.2f}. {missing}'''
  assert r"A = 1 meter. B = 2.00 meter / second. {missing}" == format_text( text, formatter='format', **context )

  # note, we have to be careful with latex commands
  text = r'''\vec{A} = {A}. \vec{B } = {B:.2f}. {missing}'''
  assert r"\vec1 meter = 1 meter. \vec{B } = 2.00 meter / second. {missing}" == format_text( text, formatter='format', **context )
