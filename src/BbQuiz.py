#! /usr/bin/env python

from Utils import *
import sys, os, re, random
import math
import yaml #, wheezy.template, asteval
import collections

import sys
sys.path.append("../externals/pyoptiontree")
import pyoptiontree


testing = 0

class BbQuiz:
    def __init__(self):
        self.quiz_data = None
        self.quiz_namespace = None
        self.correct_answer_chars = "*^!@"
        self.randomize_answers = True
        self.latex_labels = LatexLabels()

        

    def load(self, obj):
        if isinstance( obj, str ):
            if os.path.isfile( obj ):
                with open(obj) as f:
                    self.quiz_data = yaml.load( f )

                    tmp = ""
                    for (key,val) in Flattener.flatten(self.quiz_data, "", "/").items():
                        tmp += str(key)+"='"+str(val)+"'\n"
                    self.quiz_tree = pyoptiontree.PyOptionTree()
                    self.quiz_tree.addString( tmp )
            else:
                raise IOError( "argument %s does not seem to be a file" % arg )

        if isinstance( obj, dict ):
            self.quiz_data = obj

        print self.quiz_tree

        if 'latex' in self.quiz_data:
            if 'aux' in self.quiz_data['latex']:
                aux_file =  os.path.join( os.path.dirname(obj), self.quiz_data['latex']['aux']  )
                self.latex_labels.parse( aux_file )

        self.namespace = { 'global_vars' : self.quiz_data.get('vars',{} ) }
        self.namespace['global_vars'].update( self.latex_labels )
        self.namespace['global_vars']['local_vars'] = []
        for i in range(len(self.quiz_data['questions'])):
            self.namespace['global_vars']['local_vars'].append( self.quiz_data['questions'][i].get('vars',{}) )

        self.interpolate()
        self.detect_question_types()

    def detect_question_types(self):
        qnum = 0
        for question in self.quiz_data["questions"]:
            qnum += 1
            if isinstance( question.get("answer", None), dict):
                if "value" in question.get("answer", {}):
                    question["type"] = "NUM"

                if "a" in question.get("answer", {}):
                    num = 0
                    for lbl in question.get("answer", {}):
                        if( self.correct_answer_chars.find( question["answer"][lbl][0] ) >= 0 ):
                            num += 1
                    if( num == 0 ):
                        print "WARNING: question "+str(qnum)+" appears to be a multiple-choice question, but correct answer was selected."
                        question["type"] = "MC"
                    elif( num == 1 ):
                        question["type"] = "MC"
                    else:
                        question["type"] = "MA"

            if isinstance( question.get("answer", None), list ):
                question["type"] = "ORD"

            if isinstance( question.get("answer", None), bool ):
                question["type"] = "TF"

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

    #def interpolate(self):
        #for i in range(len(self.quiz_data["questions"])):
            #question = self.quiz_data["questions"][i]
            #subs = EvalTemplateDict( self.namespace )
            #subs.update( self.namespace['global_vars']['local_vars'][i] )
            #question["text"] = EvalTemplate(question["text"]).substitute(subs)

            #if isinstance( question.get("answer", None), dict):
                #for lbl in question.get("answer", {} ):
                    #question["answer"][lbl] = EvalTemplate(str(question["answer"][lbl])).substitute(subs)
            #if isinstance( question.get("answer", None), list ):
                #for i in range(len(question.get("answer", [] ) ) ):
                    #question["answer"][i] = EvalTemplate(str(question["answer"][i])).substitute(subs)



    def build_MC_tokens(self, q):
        entry = []
        entry.append( "MC" )
        entry.append( q["text"] ) 
        lbls= q["answer"].keys()
        if self.randomize_answers:
            random.shuffle(lbls)
        for lbl in  lbls:
            answer = q["answer"][lbl]
            if( self.correct_answer_chars.find( answer[0] ) >= 0 ):
                entry.append( answer[1:] )
                entry.append( "correct" )
            else:
                entry.append( answer )
                entry.append( "incorrect" )

        return entry

    def build_MA_tokens(self, q):
        entry = self.build_MC_tokens(q)
        entry[0] = "MA"

        return entry

    def build_ORD_tokens(self, q):
        entry = []
        entry.append( "ORD" )
        entry.append( q["text"] ) 
        for answer in  q["answer"]:
            entry.append( answer )

        return entry

    def build_NUM_tokens(self, q):
        entry = []
        entry.append( "NUM" )
        entry.append( q["text"] ) 
        entry.append( '{:.2E}'.format(float(q["answer"]["value"])) ) 

        if "uncertainty" in q["answer"]:
            tol = q["answer"]["uncertainty"]
        else:
            tol = "1%"

        if isinstance(tol, str) and tol.find("%") >= 0:
            tol = float(tol.replace("%",""))/100.
            tol = tol*float(q["answer"]["value"])

        tol = abs(tol)
        entry.append( '{:.2E}'.format(float(tol) ) )

        return entry

    def build_TF_tokens(self, q):
        entry = []
        entry.append( "TF" )
        entry.append( q["text"] ) 
        if q["answer"]:
            entry.append( "true" )
        else:
            entry.append( "false" )

        return entry



    def write_questions(self, filename=None):
        if not filename:
            filename = "/dev/stdout"
        with open(filename, 'w') as f:
            for question in self.quiz_data["questions"]:
                builder = getattr(self, "build_"+question["type"]+"_tokens")
                q = builder(question)
                f.write("\t".join(q)+"\n")




if __name__ == "__main__":
    for arg in sys.argv[1:]:
        quiz = BbQuiz()
        quiz.load( arg )
        quiz.write_questions(os.path.splitext(arg)[0]+".Bb")


if testing:
    print EvalTemplate("this is interpolated once ${x}").substitute( EvalTemplateDict({'x' : 10, 'y' : "${x}"}))
    print EvalTemplate("this is interpolated once ${y}").substitute( EvalTemplateDict({'x' : 10, 'y' : "${x}"}))



