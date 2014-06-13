#! /usr/bin/python2

import quik
import wheezy
import templite
import yaml
import sys, os

class latex_document:
    def __init__(self):
        self.preamble = quik.Template(
        r'''
\documentclass[letterpaper,10pt]{article}
\usepackage{amsmath}
\usepackage{amsfonts}
\usepackage{amssymb}
\usepackage{graphicx}
\usepackage{siunitx}
\usepackage[left=1in,right=1in,top=1in,bottom=1in]{geometry}

\title{@title}
        '''
        )

        self.body = quik.Template(
        r'''
\begin{document}
\maketitle
@body
\end{document}
        '''
        )

        self.question_block = quik.Template(
            r'''
\begin{enumerate}
#for @question in @questions:
\item @question
#end
\end{enumerate}
            '''
        )

    def document(self, vars):
        preamble = self.preamble.render(vars)
        body     = self.body.render( {'body':self.question_block.render(vars)} )

        doc = preamble+body

        return doc





class homework_generator:
    def __init__(config_filename):
        self.config_filename = config_filename

        self.homework_config = load( self.config_filename )


for arg in sys.argv[1:]:
    if os.path.isfile( arg ):
        with open(arg) as f:
            hw = yaml.load( f )
    else:
        raise IOError( "argument %s does not seem to be a file" % arg )


doc = latex_document()
print doc.document({"title":"Mod 01 HW", "questions" : ["What is your name?", "What is your favorite color?"]})


