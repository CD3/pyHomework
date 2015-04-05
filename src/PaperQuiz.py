#! /usr/bin/env python

from Utils import *
import sys, os, re, random
import getopt
import math
import yaml
import dpath.util
import subprocess, tempfile, shutil, shlex
from wheezy.template.engine import Engine
from wheezy.template.ext.core import CoreExtension
from wheezy.template.loader import DictLoader



latex_template= r'''
@require(config)
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
{\Large @config['title']}
\end{center}

@if len(config['instructions']) > 0:
Special Instructions:
\begin{itemize}
  @for instruction in config['instructions']:
    \item @instruction
  @end
\end{itemize}
\vspace{10pt}
@end

\begin{compactenum}
@for question in config['questions']:
    \begin{minipage}{\linewidth}
    \item @question['text']
    @if question['type'] == "MC" or question['type'] == "MA":
    \begin{compactenum}
        @for choice in question['answer']['choices']:
        \item @choice!mca
        @end
    \end{compactenum}
    @end
    @if question['type'] == "NUM":

    @question['answer']['value']!na
    @end

    \end{minipage}

    \vspace{10pt}

@end
\end{compactenum}

@if config['options'].get('make_key',False):
\clearpage
Answers:
@for answer in config['answers']:

  @answer
@end

@end

\end{document}
'''


class PaperQuiz(Quiz):
    def __init__(self):
        super( PaperQuiz, self).__init__()
        self.interpolate   = True
        self.show_answers  = False
        self.template_engine = Engine( loader=DictLoader( {'doc': latex_template} )
                                     , extensions=[CoreExtension()] )

        self.template_engine.global_vars.update({  'mca' : self.filter_multiple_choice_answer})
        self.template_engine.global_vars.update({  'saa' : self.filter_short_answer__answer})
        self.template_engine.global_vars.update({   'fa' : self.filter_formula_answer})
        self.template_engine.global_vars.update({   'na' : self.filter_numerical_answer})
        self.template_engine.global_vars.update({ 'rand' : random}                      )

        self.answers = []

    def filter_multiple_choice_answer( self, obj ):
        if isinstance( obj, str ):
          if( self.correct_answer_chars.find( obj[0] ) >= 0 ):
            if self.show_answers:
              obj = "*"+obj[1:]
            else:
              obj = obj[1:]

            # we want to generate an answer key
            # we'll do this with a pair of \label/\ref commands
            # first, create the label, then put it in the answer, then add it the answers list
            lbl = ":".join(['ans','mc',str(random.randint(0,1000))])
            obj = "".join( ['\label{',lbl,'}',obj] )
            self.answers.append( "".join([ "MC/MCA \\ref{",lbl,"}"]) )

          return obj

    def filter_numerical_answer( self, obj ):
        if isinstance( obj, str ):
          ans = obj
          if not self.show_answers:
              obj = ""
          lbl = ":".join(['ans','num',str(random.randint(0,1000))])
          obj = "".join( ['\label{',lbl,'}',obj] )
          self.answers.append( "".join([ "NUM \\ref{",lbl,"}"," : ",ans]) )
        return obj

    def filter_formula_answer( self, obj ):
        if isinstance( obj, str ):
            if not self.show_answers:
                obj = ""
        return obj

    def filter_short_answer__answer( self, obj ):
        if isinstance( obj, str ):
            if not self.show_answers:
                obj = ""
        return obj


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
          f.write( self.template_engine.get_template("doc").render( {'config': config} ) )

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


