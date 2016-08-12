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

  question = parse.Word(parse.alphas) 

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

  lines = fh.read().split('\n')
  for line in lines:

    for k,v in triggers.items():

      if re.search( v, line ):

        if not path is None:
          set( path, "".join(stage) )

        if k == 'question':
          path = [ "questions", len(get("questions")), "text" ]

        if k == 'mc_answer':
          path =[ "questions", len(get("questions"))-1, "answer", "choices" ]
          path.append( len( get(path) ) )

        if k == 'num_answer':
          path =[ "questions", len(get("questions"))-1, "answer", "value" ]

        stage = list()
        line = re.sub(v, '', line)

    stage.append(line)

    if not path is None:
      set( path, "".join(stage) )

  spec['questions'] = [ v for k,v in spec['questions'].items() ]
  for q in spec['questions']:
    if 'choices' in q['answer']:
      q['answer']['choices'] = [ v for k,v in q['answer']['choices'].items() ]
    
  
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



