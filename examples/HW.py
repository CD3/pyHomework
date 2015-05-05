#! /bin/env python
import sys
sys.path.append("../src")

from pyHomework import *



ass = HomeworkAssignment()

ass.add_question()
ass.add_text("Is this a question?")
ass.add_part()
ass.add_text("how many elements does the set of all sets that do not contian themselves contain?")
ass.add_text("NONE")


ass.write_latex()
