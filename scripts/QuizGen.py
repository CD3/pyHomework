#! /usr/bin/env python
from pyHomework.Quiz import *
from pyHomework.Emitter import *
import sys, os, re, random
from subprocess import call
import yaml
import dpath.util
import urlparse
import tempita
import argparse
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
configuration:
  make_key : True
  randomize:
    questions: True
    answers: False
  files:
    view_url  : http://example.com/files/{filename:s}
    push_url  : ssh://example.com/files/{filename:s}
    local_url : /path/to/the/files/{filename:s}

questions:
  - 
    text: "(Multiple Choice) What is the correct answer?"
    answer:
      choices:
      - '*this is the correct answer'
      - 'this is not the correct answer'
      - 'this is also not the correct answer'

  - 
    text: "(Multiple Answers) What answers are correct?"
    answer:
      choices:
      - '*this is a correct answer'
      - 'this is not a correct answer'
      - '*this is also a correct answer'

  - 
    text: "(Ordered) Put these items in the correct order"
    answer:
      ordered :
      - 'first'
      - 'second'
      - 'third'
  - 
    text: "(Numerical Answer) What is the correct number?"
    answer:
      value : 7

  - 
    text: "(Numerical Answer) What is the correct number, plus or minus 20%?"
    answer:
      value : 7
      uncertainty: 20%
  - 
    text: "(True/False) Is the answer True?"
    answer: True
  - 
    text: "(Image Example) Can you see the picture?"
    image: './picture.png'
    answer:
      choices:
        - '*yes'
        - 'no'

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

  triggers = { 'question'   : re.compile( r'^\s*\d+\.\s*' )
             , 'mc_answer'  : re.compile( r'^\s*[a-z]\.\s*' )
             , 'num_answer' : re.compile( r'^\s*answer\s*:\s*', re.IGNORECASE )
             }

  parsers = { 'question'   : parse.Suppress(parse.Word(parse.nums)+'.'+parse.White()) + parse.restOfLine
            , 'mc_answer'  : parse.Suppress(parse.Word(parse.alphas)+'.'+parse.White()) + parse.restOfLine
            , 'num_answer' : parse.Suppress(parse.White()+parse.Literal('answer:')+parse.White()) + parse.restOfLine
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

    # if we have a match, we need to clear the stage
    matched = matches(line)
    if matched and path:
      set( path, "".join(stage) )
      stage = list()

    try: # check for config vars
      var,val = parsers['config_var'].parseString(line)
      # will just set config parameter directly and continue
      dpath.util.new( spec, var.lower(), val )
      path = None
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


  print yaml.dump(spec,default_flow_style=False)
  spec = dict2list(spec)
  # spec['questions'] = [ v for k,v in spec['questions'].items() ]
  # for q in spec['questions']:
    # if 'choices' in q['answer']:
      # q['answer']['choices'] = [ v for k,v in q['answer']['choices'].items() ]
    
  print yaml.dump(spec,default_flow_style=False)
  
  return spec




if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Generate quiz in various format from YAML or Markdown.')
  parser.add_argument('quiz_file', nargs='+', help="Quiz input files to be processed.")
  parser.add_argument('--example', '-e', action='store_true', help="Write an example quiz input file.")
  parser.add_argument('--override', '--config-var', '-c',  help="Specify configuration overrides.")
  parser.add_argument('--list-config', '-l', action='store_true', help="Output configuration option (for debugging).")
  parser.add_argument('--output', '-o', help="Output filename. Default is to replace extenstoin of spec file with extension of output format.")
  parser.add_argument('--type', '-t', default='bb', help="Output file format. Default is bb (blackboard).")

  args = parser.parse_args()


  if args.example:
    with open( args.example, 'w' ) as f:
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

      quiz.load( spec )

    overrides = make_overrides( args.override )
    for k,v in overrides.items():
      v = eval(v)
      print "Overriding '%s': '%s' -> '%s'" % (k,quiz.config(k,None),v)
      quiz.config(k,value=v)

    if args.list_config:
      print quiz._config

    outfile = get_fn( fn, args.type )
    if args.output:
      outfile = args.output
    quiz.write(outfile)



