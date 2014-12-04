#! /usr/bin/env python

from Utils import *
import sys, os, re, random
import math
import yaml
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
\usepackage[left=1in,right=1in,top=1in,bottom=1in]{geometry}

\title{@title}

\begin{document}
\maketitle

\begin{enumerate}
@for question in questions:
    \item @question['tex']
    @if question['type'] == "SA":
    \vspace{1in}
    @question['answer']['tex']!saa
    \vspace{1in}
    @end
    @if question['type'] == "FORMULA":
    \vspace{1in}
    @question['answer']['tex']!fa
    \vspace{1in}
    @end
    @if question['type'] == "NUM":
    \vspace{1in}
    @question['answer']['tex']!na
    \vspace{1in}
    @end
    @if question['type'] == "MC":
    \begin{enumerate}
        @for lbl,answer in question['answer'].iteritems():
        \item @answer!mca
        @end
    \end{enumerate}
    @end
@end
\end{enumerate}

\end{document}
'''


class PaperQuiz:
    def __init__(self):
        super( PaperQuiz, self).__init__()
        self.show_answers      = True
        self.template_engine = Engine( loader=DictLoader( {'doc': latex_template} )
                                     , extensions=[CoreExtension()] )

        self.template_engine.global_vars.update({'mca' : self.filter_multiple_choice_answer})
        self.template_engine.global_vars.update({'saa' : self.filter_short_answer__answer})
        self.template_engine.global_vars.update({ 'fa' : self.filter_formula_answer})
        self.template_engine.global_vars.update({ 'na' : self.filter_numerical_answer})

    def format_answers(self):
        for question in self.quiz_data["questions"]:
            if isinstance( question.get("answer", None), dict):
                if question["type"] == "NUM":
                    if "value" in question["answer"]:
                        question["answer"]["tex"] = question["answer"]["value"]
                        if "uncertainty" in question["answer"]:
                            question["answer"]["tex"] += " \pm "
                            question["answer"]["tex"] += question["answer"]["uncertainty"]

                if question["type"] == "FORMULA":
                    if "formula" in question["answer"]:
                        question["answer"]["tex"] = question["answer"]["formula"]
                if question["type"] == "SA":
                    if "idea" in question["answer"]:
                        question["answer"]["tex"] = question["answer"]["idea"]

    # filters
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
        if not filename:
            filename = "/dev/stdout"
        with open(filename, 'w') as f:
            f.write( self.template_engine.get_template("doc").render( self.quiz_data ) )

    def compile_latex(self, filename):
        basename = os.path.splitext(arg)[0]
        pdf      = basename+".pdf"
        cwd = os.getcwd()
        temp = tempfile.mkdtemp()

        
        shutil.copy( filename, temp )
        os.chdir( temp )

        ret = subprocess.call(shlex.split( 'pdflatex --interaction=batchmode '+basename) )
        ret = subprocess.call(shlex.split( 'pdflatex --interaction=batchmode '+basename) )
        ret = subprocess.call(shlex.split( 'bibtex '+basename) )
        ret = subprocess.call(shlex.split( 'pdflatex --interaction=batchmode '+basename) )

        shutil.copy( pdf, cwd)
        os.chdir( cwd)


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        quiz = PaperQuiz()
        quiz.load( arg )
        quiz.write_questions( os.path.splitext(arg)[0]+".tex" )
        quiz.compile_latex( os.path.splitext(arg)[0]+".tex" )


