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
\uepackage{amsmath}
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
    \item @question['text']
    @if question['type'] == "SA":
    \vspace{2in}
    @end
    @if question['type'] == "MC":
    \begin{enumerate}
        \item answer
    \end{enumerate}
    @end
@end
\end{enumerate}

\end{document}
'''


class PaperQuiz:
    def __init__(self):
        self.quiz_data = None
        self.quiz_namespace = None
        self.correct_answer_chars = "*^!@"
        self.randomize_answers = True
        self.questions_answers = True
        self.template_engine = Engine( loader=DictLoader( {'doc': latex_template} )
                                     , extensions=[CoreExtension()] )

        

    def load(self, obj):
        if isinstance( obj, str ):
            if os.path.isfile( obj ):
                with open(obj) as f:
                    self.quiz_data = yaml.load( f )
            else:
                raise IOError( "argument %s does not seem to be a file" % arg )

        if isinstance( obj, dict ):
            self.quiz_data = obj

        for i in range(len(self.quiz_data['questions'])):
            self.quiz_data['questions'][i]['id'] = random.randint(0,100000)

        self.namespace = { 'global_vars' : self.quiz_data.get('vars',{} ) }
        self.namespace['global_vars']['local_vars'] = []
        for i in range(len(self.quiz_data['questions'])):
            self.namespace['global_vars']['local_vars'].append( self.quiz_data['questions'][i].get('vars',{}) )
            
        self.interpolate()
        self.detect_question_types()

    def detect_question_types(self):

        for question in self.quiz_data["questions"]:
            if isinstance( question.get("answer", None), dict):
                if "value" in question.get("answer", {}):
                    question["type"] = "NUM"

                if "a" in question.get("answer", {}):
                        question["type"] = "MC"

                if "formula" in question.get("answer", {}):
                        question["type"] = "FORM"

                if "idea" in question.get("answer", {}):
                        question["type"] = "SA"

    def interpolate(self, tree = None, subs = None):
        '''Interpolate variable references in entire document.
           We interpolate all strings in the document, but only interpolate
           from variables defined under var nodes.'''

        if tree == None:
            tree = self.quiz_data
            subs = EvalTemplateDict( self.namespace )
            subs.update( self.namespace['global_vars'] )
            for k in tree:
                if isinstance( tree[k], str ):
                    tree[k] = EvalTemplate(tree[k]).substitute(subs)

                if k != "questions":
                    self.interpolate( tree[k], subs )

            for i in range(len(self.quiz_data["questions"])):
                question = self.quiz_data["questions"][i]
                subs = EvalTemplateDict( self.namespace )
                subs.update( self.namespace['global_vars']['local_vars'][i] )

                self.interpolate( question, subs )
        else:
            if isinstance(tree, dict):
                for k in tree:
                    if isinstance( tree[k], str ):
                        tree[k] = EvalTemplate(tree[k]).substitute(subs)
                    else:
                        self.interpolate(tree[k],subs)

            elif isinstance(tree, list):
                for i in range(len(tree)):
                    if isinstance( tree[i], str ):
                        tree[i] = EvalTemplate(tree[i]).substitute(subs)
                    else:
                        self.interpolate(tree[i],subs)
                    
                    



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


