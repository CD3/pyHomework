#! /usr/bin/env python

import sys, os, re, random
from string import Template
import math
import yaml
import wheezy.template as wt



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
    \item @question.text
@end
\end{enumerate}

\end{document}
'''


class InterpEvalError(KeyError):
    pass

class InterpDict(dict):
    def __getattr__(self,attr):
        return self.get(attr)
    __setattr__=dict.__setitem__
    __delattr__=dict.__delitem__

    def __getitem__(self,key):
        try:
            return dict.__getitem__(self,key)
        except KeyError:
            try:
                return eval(key,self)
            except Exception, e:
                raise InterpEvalError(key,e)

class PaperQuiz:
    def __init__(self):
        self.quiz_data = None
        self.quiz_namespace = None
        self.correct_answer_chars = "*^!@"
        self.randomize_answers = True
        self.questions_answers = True

        self.latex_template = wt.Engine( loader=wt.DictLoader( {'doc', latex_template} )
                                     , extensions=[wt.CoreExtension()] )

        

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

        self.namespace = { 'global' : self.quiz_data.get('vars',{} ) }
        self.namespace['global']['locals'] = []
        for i in range(len(self.quiz_data['questions'])):
            self.namespace['global']['locals'].append( self.quiz_data['questions'][i].get('vars',{}) )
            
        self.interpolate()
        self.detect_question_types()

        print self.namespace

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

    def interpolate(self):
        pass

    def write_MC_question(self, q):
        text = ""
        return text

    def write_NUM_question(self, q):
        text = ""
        return text

    def write_FORM_question(self, q):
        text = ""
        return text

    def write_SA_question(self, q):
        text = ""
        return text


    def write_questions(self, filename=None):

        return 
        if not filename:
            filename = "/dev/stdout"
        with open(filename, 'a') as f:
            for question in self.quiz_data["questions"]:
                builder = getattr(self, "build_"+question["type"]+"_tokens")
                q = builder(question)
                f.write("\t".join(q)+"\n")




if __name__ == "__main__":
    for arg in sys.argv[1:]:
        quiz = PaperQuiz()
        quiz.load( arg )
        quiz.write_questions(os.path.splitext(arg)[0]+".tex")


#engine = wt.Engine( loader=wt.DictLoader({'x': 
