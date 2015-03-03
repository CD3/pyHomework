#! /usr/bin/env python

from Utils import *
import sys, os, re, random
import math
import yaml
import dpath.util
import subprocess, tempfile, shutil, shlex
from wheezy.template.engine import Engine
from wheezy.template.ext.core import CoreExtension
from wheezy.template.loader import DictLoader



latex_template= r'''
@require(title,questions)
\documentclass[letterpaper,10pt]{article}
\usepackage{amsmath}
\usepackage{amsfonts}
\usepackage{amssymb}
\usepackage{graphicx}
\usepackage{siunitx}
\usepackage{paralist}
\usepackage[left=0.5in,right=0.5in,top=0.5in,bottom=0.5in]{geometry}


\begin{document}
\center{\Large @title}

\begin{compactenum}
@for question in questions:
    \begin{minipage}{\linewidth}
    \item @question['text']
    @if question['type'] == "MC":
    \begin{compactenum}
        @for choice in question['answer']['choices']:
        \item @choice
        @end
    \end{compactenum}
    \end{minipage}

    \vspace{10pt}

    @end
@end
\end{compactenum}

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

    def filter_multiple_choice_answer( self, obj ):
        if isinstance( obj, str ):
            if( self.correct_answer_chars.find( obj[0] ) >= 0 ):
                if self.show_answers:
                    obj = "*"+obj[1:]
                else:
                    obj = obj[1:]

        return obj

    def filter_numerical_answer( self, obj ):
        if isinstance( obj, str ):
            if not self.show_answers:
                obj = ""
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
        quiz_data = extractDict(self.quiz_tree)

        # replace the questions dict with questions list so we can sort and shuffle
        questions = [None]*len( quiz_data['questions'] )
        for k in quiz_data['questions']:
          # we can't just append here because we won't get the index numbers in order
          questions[int(k)] = quiz_data['questions'][k] # this assumes no questoin numbers are skipped. should be safe.
        quiz_data['questions'] = questions

        # now do the same thing for the answers in all questions (ONLY WORKS FOR MULTIPLE CHOICE CURRENTLY)
        for question in quiz_data['questions']:
          choices = [None]*len(question['answer']['choices'])
          for k in question['answer']['choices']:
            choices[int(k)] = question['answer']['choices'][k]
          question['answer']['choices'] = choices

        if quiz_data.get('options',{}).get('randomize',{}).get('questions',False):
          random.shuffle( quiz_data['questions'] )

        if quiz_data.get('options',{}).get('randomize',{}).get('answers',False):
          for question in quiz_data['questions']:
            random.shuffle(question['answer']['choices'])


        if not filename:
            filename = "/dev/stdout"
        with open(filename, 'w') as f:
            f.write( self.template_engine.get_template("doc").render( quiz_data ) )

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
        ret = subprocess.call(shlex.split( 'latexmk -pdf '+basename) )

        shutil.copy( pdf, cwd)
        os.chdir( cwd)


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        quiz = PaperQuiz()
        quiz.load( arg )
        quiz.write_questions( os.path.splitext(arg)[0]+".tex" )
        quiz.compile_latex( os.path.splitext(arg)[0]+".tex" )


