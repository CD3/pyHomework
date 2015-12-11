#! /usr/bin/env python
"""
  BbQuiz: generate Blackboard quizzes from YAML spec files.

  Usage:
    BbQuiz.py [-l] [-c STR]... [-t TYPE] [-o FILE] <quiz-file> ...
    BbQuiz.py -m
    BbQuiz.py -e FILE

  Options:
    -e FILE, --example FILE                     write an example quiz file and exit.
    -c STR, --config-var STR, --override STR    specify a configuration override.
    -l, --list-config                           list configuration options (for debug).
    -o, --output FILE                           write output to FILE. default is to replace extention of spec file with .txt
    -t TYPE, --type TYPE                        output type [default: bb]


"""

from pyHomework.Quiz import *
from pyHomework.Emitter import *
import sys, os, re, random
from subprocess import call
import yaml
import dpath.util
import urlparse
import tempita


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



class BbQuiz(Quiz):
    def __init__(self,*args,**kwargs):
      super(BbQuiz,self).__init__(*args,**kwargs)
      self._config = { 'files' :
                         { 'view_url'  : 'http://example.com/files/{filename:s}'
                         , 'push_url'  : 'ssh://example.com/files/{filename:s}'
                         , 'local_url' : '/path/to/the/files/{filename:s}'
                         }
                    , 'randomize' :
                        { 'questions' : False
                        , 'answers'   : False
                        }
                    }

    def push_image(self, image_filename, remote_config):
        data = dict()

        if 'copy_root' in remote_config:
          url = urlparse.urlparse( os.path.join( remote_config['copy_root'], remote_config['image_dir'] ) )
        else:
          return None

        if url.scheme == 'ssh':
          data['file']   = image_filename
          data['netloc'] = url.netloc
          data['path']   = url.path[1:]

          cmd = 'scp "%(file)s" "%(netloc)s:%(path)s" > /dev/null' % data
          print "found file/link pair. copying file to server with '%s'." % cmd
          os.system( cmd )
        
        # the link that points to the image may not be the same as the url we copied it too, so we want to construct the
        # correct link and return it.
        link = urlparse.urljoin( remote_config['web_root'], os.path.join(remote_config['image_dir'], os.path.basename(image_filename) ) )
        return link

    def write_quiz(self, filename="/dev/stdout"):
      with open(filename, 'w') as f:
        f.write( self.emit(BbEmitter) )


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

    def write_quiz(self, filename="/dev/stdout"):
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
        



























if __name__ == "__main__":

  from docopt import docopt
  arguments = docopt(__doc__, version='0.1')

  if not arguments['--example'] is None:
    with open( arguments['--example'], 'w' ) as f:
      f.write( example_spec )
    sys.exit(0)

  for arg in arguments['<quiz-file>']:
    if arguments['--type'].lower() == 'bb':
      quiz = BbQuiz()
    elif arguments['--type'].lower() == 'latex':
      quiz = LatexQuiz()
    elif arguments['--type'].lower() == 'pdf':
      quiz = LatexQuiz()
    else:
      quiz = BbQuiz()


    with open(arg,'r') as f:
      quiz.load( yaml.load(f) )

    overrides = make_overrides( arguments['--override'] )
    for k,v in overrides.items():
      v = eval(v)
      print "Overriding '%s': '%s' -> '%s'" % (k,quiz.config(k,None),v)
      quiz.config(k,value=v)

    if arguments['--list-config']:
      print quiz._config

    outfile = get_fn( arg, arguments['--type'] )
    if arguments['--output'] is not None:
      outfile = arguments['--output']
    quiz.write_quiz(outfile)



