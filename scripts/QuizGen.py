#! /usr/bin/env python
"""
  BbQuiz: generate Blackboard quizzes from YAML spec files.

  Usage:
    BbQuiz.py [-l] [-c STR]... [-o FILE]<quiz-file> ...
    BbQuiz.py -m
    BbQuiz.py -e FILE

  Options:
    -e FILE, --example FILE                     write an example quiz file and exit.
    -c STR, --config-var STR, --override STR    specify a configuration override.
    -l, --list-config                           list configuration options (for debug).
    -o, --output FILE                           write output to FILE. default is to replace extention of spec file with .txt


"""

from pyHomework.Quiz import *
import sys, os, re, random
import yaml
import dpath.util
import urlparse


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

    def write_quiz(self, filename="/dev/stdout"):
      with open(filename, 'w') as f:
        f.write( self.emit('bb') )

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

class LatexQuiz(Quiz):
    def __init__(self,*args,**kwargs):
      super(BbQuiz,self).__init__(*args,**kwargs)
      self._config = { 'make_key' : False
                     , 'randomize' :
                        { 'questions' : False
                        , 'answers'   : False
                        }
                    }

      template = r'''
<%!
    import random
    import collections

    answers = collections.OrderedDict()
%>

<%
    def mca( text ):
      if isAns( text ):
        text = text[1:]
      return text

    def isAns( text ):
      return special_chars['correct_answer'].find( text[0] ) >= 0
%>



\documentclass[letterpaper,10pt]{article}
\usepackage{amsmath}
\usepackage{amsfonts}
\usepackage{amssymb}
\usepackage{graphicx}
\usepackage{siunitx}
\usepackage{paralist}
\usepackage[left=0.5in,right=0.5in,top=0.5in,bottom=0.5in]{geometry}


\begin{document}
\begin{center}
{\Large ${title}}
\end{center}

%if not instructions is UNDEFINED:
Special Instructions:
\begin{itemize}
  %for instruction in instructions:
    \item ${instruction}
  %endfor
\end{itemize}
\vspace{10pt}
Questions:
\vspace{10pt}
%endif

\begin{compactenum} <% i = 0 %>
%for question in questions:
<%
  i += 1
  qlbl = '\label{%d}' % i
  qref = qlbl.replace("label", "ref")
  answers[qref] = []
%>\begin{minipage}{\linewidth}
    \item ${qlbl} ${question['text']}
    %if question['type'] == "MC" or question['type'] == "MA":
    \begin{compactenum} <% j = 0 %>
        %for choice in question['answer']['choices']:
        <% 
          j += 1
          plbl = '\label{%d%d}' % (i,j)
          pref = plbl.replace("label", "ref")
          if isAns( choice ):
            answers[qref].append( pref )
        %>\item ${plbl} ${choice|mca}
        %endfor
    \end{compactenum}
    %endif
    %if question['type'] == "TF":

        True \hskip 1cm False
    %endif
    <%
      if question['type'] == "NUM":
        answers[qref].append( str( question['answer']['value'] ) )
        answers[qref][-1] +=  str( question['answer'].get('unit', "") )

      if question['type'] == "TF":
        answers[qref].append( "True" if question['answer'] else "False" )
    %>
    \end{minipage}

    \vspace{10pt}

%endfor
\end{compactenum}

%if make_key:
\clearpage
Key - Quiz Answers:
\begin{itemize}
  %for k in answers:
      \item ${k}.
    %for v in answers[k]:
            ${v} 
    %endfor
  %endfor

\end{itemize}
%endif

\end{document}
'''




























if __name__ == "__main__":

  from docopt import docopt
  arguments = docopt(__doc__, version='0.1')

  if not arguments['--example'] is None:
    with open( arguments['--example'], 'w' ) as f:
      f.write( example_spec )
    sys.exit(0)

  for arg in arguments['<quiz-file>']:
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

    outfile = os.path.splitext(arg)[0]+".txt"
    if arguments['--output'] is not None:
      outfile = arguments['--output']
    quiz.write_quiz(outfile)



