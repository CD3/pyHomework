#! /usr/bin/env python

# local modules
from pyHomework.Quiz import *
from pyHomework.Emitter import *


# standard modules
import sys, os, re, random, StringIO
from subprocess import call
import argparse

# non-standard modules
import dpath.util
import yaml
import tempita
import pyparsing as parse


def make_overrides( override ):
  if isinstance(override,(str,unicode)):
    key,val = re.split( "\s*=\s*", override)
    return {key: val}
  if isinstance(override,list):
    tmp = dict()
    for o in override:
      tmp.update( make_overrides(o) )
    return tmp
  return {}

def get_fn( inputfn, type ):
  basename = os.path.splitext(inputfn)[0]
  if type.lower() == 'bb':
    return basename + '.txt'
  if type.lower() == 'latex':
    return basename + '.tex'
  if type.lower() == 'pdf':
    return basename + '.pdf'

  return basename + '.' + type

example_spec = '''
title : Quiz
configuration/make_key : True
configuration/randomize/questions: True
configuration/randomize/answers: False

# this is a comment. comments are ignored

# multiple choice questions are written with the possible
# answeres listed below. the correct answer is marked with a ^
1. (Multiple Choice) What is the correct answer?
   a. ^this is the correct answer
   b. this is not the correct answer
   c. this is also not the correct answer

# more than one answer may be correct.
2. (Multiple Answers) What answers are correct?
   a. ^this is a correct answer
   a. this is not a correct answer
   a. ^this is also a correct answer

# numerical answer questions have a... numerical answer.
# by default, a 1% tolerance will be used.
1. (Numerical Answer) What is the correct number?
   answer : 7

# the tolerance can be specified
1. (Numerical Answer) Enter any number between 8 and 12.
   answer : 10 +/- 2

# you can also put units in the answer. a statement that indicates what units the answer
# should be given will automatically be generated and appended to the question.
1. (Numerical Answer) How long is a football field?
   answer : 100 yd

# images can be loaded
1. Images can be included with the include graphics command: \includegraphics{./filename.png}
   They are embedded directly into the quiz file, so there is no chance of a broken link.
   a. ^yes
   b. no

1. Remote images can be specified by their url \includegraphics[fmt=png]{https://www.google.com/logos/doodles/2016/2016-doodle-fruit-games-day-11-5698592858701824-scta.png}.
   The image will be downloaded and embedded into the quiz file just like a local image.
   a. ^yes
   b. no
'''




class LatexQuiz(Quiz):
    def __init__(self,*args,**kwargs):
      super(LatexQuiz,self).__init__(*args,**kwargs)
      self._default_config = { 'make_key' : False
                             , 'randomize' :
                               { 'questions' : False
                               , 'answers'   : False
                               } }
      self._config = self._default_config.copy()

      self.template = r'''
{{default instructions = 'UNDEFINED'}}
{{default make_key = False}}
\documentclass[letterpaper,10pt]{article}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{siunitx}
\usepackage{paralist}
\usepackage[left=0.5in,right=0.5in,top=0.5in,bottom=0.5in]{geometry}

\begin{document}
\begin{center}
{\Large {{title}}}
\end{center}

{{if instructions != 'UNDEFINED'}}
Special Instructions:
{{instructions}}
\vspace{10pt}
Questions:
\vspace{10pt}
{{endif}}

{{questions}}

{{if make_key}}
\clearpage
Answers:

{{key}}

{{endif}}

\end{document}
'''

    def write(self, filename="/dev/stdout"):
      engine = tempita.Template(self.template)
      render_data = { 'questions'    : self.emit(LatexEmitter('compactenum',labels=True))
                    , 'key'          : self.emit(LatexKeyEmitter()) }
      render_data.update( self._config )
      text = engine.substitute( **render_data )

      if filename.endswith('.pdf'):
        texfile = get_fn( filename, 'tex' )
      else:
        texfile = filename

      with open(texfile, 'w') as f:
        f.write( text )

      if filename.endswith( '.pdf' ):
        call( ['latexmk', '-pdf', texfile ] )
        call( ['latexmk', '-c', texfile ] )
        






















def parse_markdown( fh ):

  parsers = { 'question'   : parse.Suppress(parse.Word(parse.nums)+'.'+parse.White()) + parse.restOfLine
            , 'mc_answer'  : parse.Suppress(parse.Word(parse.alphas)+'.'+parse.White()) + parse.restOfLine
            , 'num_answer' : parse.Suppress(parse.White()+parse.Literal('answer')+parse.Optional(parse.White())+':') + parse.restOfLine
            , 'config_var' : parse.Word(parse.alphanums+'/_')+parse.Suppress(':'+parse.White())+parse.restOfLine
            }


  spec = dict()
  path = None
  stage = list()

  def get(path):
    vals = dpath.util.values(spec, path)
    if len(vals) > 0:
      return vals[0]
    return {}

  def set(path, v):
    return dpath.util.new(spec, path, v)

  def matches( line ):
    matches = 0
    for k in parsers:
      try:
        parsers[k].parseString(line)
        matches += 1
      except:
        pass

    return matches > 0

  lines = fh.read().split('\n')
  lines.append("finished: true") # this will make sure that the last stage is cleared.
  for line in lines:

    # remove comments
    line = re.sub('\s*[^#]*#.*$','',line)

    # if we have a match, we need to clear the stage
    matched = matches(line)
    if matched and path:
      set( path, "".join(stage) )
      stage = list()

    try: # check for config vars
      var,val = parsers['config_var'].parseString(line)
      if not var == 'answer':
        # will just set config parameter directly and continue
        dpath.util.new( spec, var.lower(), val )
        continue

    except:
      pass

    try: # check for beginning of question
      line = parsers['question'].parseString(line)[0]
      path = [ "questions", len(get("questions")), "text" ]
    except:
      pass

    try: # check for beginning of multiple-choice answer
      line = parsers['mc_answer'].parseString(line)[0]
      path =[ "questions", len(get("questions"))-1, "answer", "choices" ]
      path.append( len( get(path) ) )
    except:
      pass

    try: # check for numerical answer
      line = parsers['num_answer'].parseString(line)[0]
      path =[ "questions", len(get("questions"))-1, "answer", "value" ]
    except:
      pass

    if line:
      stage.append(line)

  def dict2list(d):

    if isinstance(d,list):
      # if d is already a list, then just convert its children
      for i in range(len(d)):
        d[i] = dict2list(d[i])
      return d

    if isinstance(d,dict):
      # convert dict to list if all of its keys are integers
      # but make sure to convert all of its entries first
      islist = True
      for k in d:
        d[k] = dict2list(d[k])
        if not isinstance(k,int):
          islist = False
      if islist:
        return [ d[k] for k in sorted(d.keys()) ]

    return d


  spec = dict2list(spec)
  
  return spec




if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Generate quiz in various format from YAML or Markdown.')
  parser.add_argument('quiz_file', nargs='*', help="Quiz input files to be processed.")
  parser.add_argument('--example', '-e', action='store_true', help="Write an example quiz input file.")
  parser.add_argument('--override', '--config-var', '-c',  help="Specify configuration overrides.")
  parser.add_argument('--output', '-o', help="Output filename. Default is to replace extenstion of spec file with extension of output format.")
  parser.add_argument('--type', '-t', default='bb', help="Output file format. Default is bb (blackboard).")
  parser.add_argument('--debug', '-d', action='store_true', help="Output debug information.")

  args = parser.parse_args()


  if args.example:
    with open( args.quiz_file[0], 'w' ) as f:
      f.write( example_spec )
    sys.exit(0)

  for fn in args.quiz_file:
    if args.type.lower() == 'bb':
      quiz = BbQuiz()
    elif args.type.lower() == 'latex':
      quiz = LatexQuiz()
    elif args.type.lower() == 'pdf':
      quiz = LatexQuiz()
    else:
      quiz = BbQuiz()


    with open(fn,'r') as f:
      ext = os.path.splitext(fn)[1]
      if ext == '.md':
        spec = parse_markdown(f)
      if ext == '.yaml':
        spec = yaml.load(f)

    try:
      quiz.load( spec )
    except KeyError as e:
      print "ERROR: There was a problem parsing the quiz file."
      print "       Please make sure that the file is formatted correctly."
      print "       Note: add the --debug option to see the tree that was read"
      if args.debug:
        print yaml.dump(spec)
      sys.exit(1)


    overrides = make_overrides( args.override )
    for k,v in overrides.items():
      v = eval(v)
      print "Overriding '%s': '%s' -> '%s'" % (k,quiz.config(k,None),v)
      quiz.config(k,value=v)

    if args.debug:
      print quiz._config

    outfile = get_fn( fn, args.type )
    if args.output:
      outfile = args.output


    quiz.write(outfile)



