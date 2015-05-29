#! /usr/bin/env python

from Utils import *
import sys, os, re, random
import getopt
import math
import yaml
import dpath.util
import subprocess, tempfile, shutil, shlex
from mako.template import Template



latex_template= r'''
<%!
    correct_answer_chars = "*^!@"
    answers = dict()
    def mca( text ):
      if isAns( text ):
        text = text[1:]
      return text

    def isAns( text ):
      return correct_answer_chars.find( text[0] ) >= 0
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
{\Large ${config['title']}}
\end{center}

%if len(config['instructions']) > 0:
Special Instructions:
\begin{itemize}
  %for instruction in config['instructions']:
    \item ${instruction}
  %endfor
\end{itemize}
\vspace{10pt}
%endif

\begin{compactenum}
%for question in config['questions']:
    \begin{minipage}{\linewidth}
    \item ${question['text']}
    %if question['type'] == "MC" or question['type'] == "MA":
    \begin{compactenum}
        %for choice in question['answer']['choices']:
        \item ${choice|mca}
        <%doc>
        %if isAns(choice):
        %endif
        </%doc>
        %endfor
    \end{compactenum}
    %endif
    %if question['type'] == "NUM":
    <%doc> ${question['answer']['value']} </%doc>
    %endif
    \end{minipage}

    \vspace{10pt}

%endfor
\end{compactenum}

%if config['options'].get('make_key',False):
\clearpage
Answers:
%for answer in config['answers']:

  ${answer}
%endfor

%endif

\end{document}
'''


class PaperQuiz(Quiz):
    def __init__(self):
        super( PaperQuiz, self).__init__()
        self.interpolate   = True
        self.show_answers  = False
        self.template_engine = Template(latex_template )


        self.answers = []



    def write_questions(self, filename=None):
        config = extractDict(self.quiz_tree)

        # setup options tree, take care of defaults
        config['options'] = config.get('options',{})

        self.show_answers = config['options'].get('show_answers',False)







        # add an empty instructions entry if non exists
        config['instructions'] = config.get('instructions',{})


        # replace questions, 
        config['questions']    = dict2list( config['questions'] )
        config['instructions'] = dict2list( config['instructions'] )

        # now do the same thing for the answers to MC questions
        for question in config['questions']:
          if question.get('answer',{}).get('choices',{}):
            question['answer']['choices'] = dict2list( question['answer']['choices'] )

        # randomize questions and answers
        if config.get('options',{}).get('randomize',{}).get('questions',False):
          random.shuffle( config['questions'] )

        if config.get('options',{}).get('randomize',{}).get('answers',False):
          for question in config['questions']:
            random.shuffle(question['answer']['choices'])

        config['answers'] = self.answers

        #import pprint
        #pprint.pprint(config['questions'])

        if not filename:
            filename = "/dev/stdout"
        with open(filename, 'w') as f:
          f.write( self.template_engine.render( config=config ) )

    def compile_latex(self, filename):
        basename = os.path.splitext(arg)[0]
        pdf      = basename+".pdf"
        cwd = os.getcwd()
        temp = tempfile.mkdtemp()

        
        shutil.copy( filename, temp )
        os.chdir( temp )

        #ret = subprocess.call(shlex.split( 'pdflatex --interaction=batchmode '+basename) )
        #ret = subprocess.call(shlex.split( 'pdflatex --interaction=batchmode '+basename) )
        #ret = subprocess.call(shlex.split( 'bibtex '+basename) )
        #ret = subprocess.call(shlex.split( 'pdflatex --interaction=batchmode '+basename) )
        with open(os.devnull,'w') as FNULL:
          ret = subprocess.call(shlex.split( 'latexmk -pdf '+basename), stdout=FNULL, stderr=subprocess.STDOUT)


        shutil.copy( pdf, cwd)
        os.chdir( cwd)

    def preview_pdf(self, filename):
      with open(os.devnull,'w') as FNULL:
        viewer = opts.get('-P', 'evince')
        ret = subprocess.call([viewer,filename], stdout=FNULL, stderr=subprocess.STDOUT)


if __name__ == "__main__":
    try:
      optlist,args = getopt.getopt(sys.argv[1:], "pP:" )
      opts = dict()
      for o,a in optlist:
        opts[o] = a if  a else True

    except getopt.GetoptError as err:
      print str(err)
      sys.exit(1)

    for arg in args:
      basename = os.path.splitext(arg)[0]
      quiz = PaperQuiz()
      quiz.load( arg )
      quiz.write_questions( basename+".tex" )
      quiz.compile_latex(   basename+".tex" )
      if opts.get('-p', False) or opts.get('-P', False):
        quiz.preview_pdf(     basename+".pdf" )


