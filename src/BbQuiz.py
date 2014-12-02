#! /usr/bin/env python

from Utils import *
import sys, os, re, random
import math
import yaml #, wheezy.template, asteval
import collections
from dpath import util
import pprint

import sys
sys.path.append("../externals/pyoptiontree")
import pyoptiontree


testing = 0


def interpolate(self, fromtree = None):
    if fromtree == None:
        fromtree = self

    for (name, branch) in self.items():
        if isinstance( branch, str ):
            pairs = FindPairs(branch, '${','}')
            orig = branch
            for i in range(len(pairs)):
                pair = pairs[i]
                link = branch[ pair[1][0]:pair[1][1]+1 ]
                repl = fromtree( link )
                branch = branch[:pair[0][0]] + repl + branch[pair[0][1]+1:]

                shift = (pair[0][1]+1 - pair[0][0]) - len(repl)
                for j in range(i+1,len(pairs)):
                    pairs[j][0][0] -= shift
                    pairs[j][0][1] -= shift
                    pairs[j][1][0] -= shift
                    pairs[j][1][1] -= shift

                self.set(name,branch)

                if branch != orig:
                  pass
                  # recursive interpolation is going to be tricky here. not ready yet.
                  #self.interpolate( fromtree(link + "/.." ) )

        elif isinstance( branch, pyoptiontree.PyOptionTree):
            branch.interpolate()

pyoptiontree.PyOptionTree.__dict__['interpolate'] = interpolate

def toBool( v ):
    if isinstance(v,str):
      isTrue  = str(v).lower() in ('true', 'yes','1')
      isFalse = str(v).lower() in ('false','no','0')

      if isTrue:
          return True
      if isFalse:
          return False

    if isinstance(v,int):
        return not v == 0

    return False


def FindPairs( s, beg_str, end_str):
    curr = 0

    pairs = list()
    run = True
    while run:
        opair = None
        curr = s.find( beg_str, curr )
        beg = curr
        curr = s.find( end_str, curr )
        end = curr
        if beg >= 0 and end > 0:
            opair = [beg,end]

        if opair:
            ipair = [
            opair[0] + len(beg_str)
           ,opair[1] - len(end_str)
            ]

            pairs.append( [opair,ipair] )

        else:
            run = False

    return pairs

class BbQuiz:
    def __init__(self):
        self.quiz_tree = None
        self.quiz_namespace = None
        self.correct_answer_chars = "*^!@"
        self.randomize_answers = True
        self.latex_labels = LatexLabels()

    def load(self, obj):
        if isinstance( obj, str ):
            if os.path.isfile( obj ):
                with open(obj) as f:
                    self.quiz_tree = yaml.load( f )
            else:
                raise IOError( "argument %s does not seem to be a file" % arg )

        if isinstance( obj, dict ):
            self.quiz_tree = obj


        if 'latex' in self.quiz_tree:
            if 'aux' in self.quiz_tree['latex']:
                aux_file =  os.path.join( os.path.dirname(obj), self.quiz_tree['latex']['aux']  )
                self.latex_labels.parse( aux_file )

        for key in self.latex_labels:
          pass

        if not 'vars' in self.quiz_tree:
          self.quiz_tree['vars'] = dict()
        self.quiz_tree['vars'].update( self.latex_labels )

        
        tmp = ""
        for (key,val) in Flattener.flatten(self.quiz_tree, "", "/").items():
            tmp += str(key)+"='"+str(val)+"'\n"
        self.quiz_tree = pyoptiontree.PyOptionTree()
        self.quiz_tree.addString( tmp )
        self.quiz_tree.interpolate()

        self.detect_question_types()

    def detect_question_types(self):
        def isBool(v):
          return str(v).lower() in ('true', 'yes','false','no','0','1')

        for (qnum,question) in self.quiz_tree("questions").items():
            qnum = int(qnum) + 1

            # if the question has an answer that is a subtree, we need to figure out what kind of question it is
            if isinstance( question.get("answer", None), pyoptiontree.PyOptionTree):

                # if the answer has an element named "value", then the question is numerical
                if question.get("answer").get("value", None):
                    question.set("type", "NUM")

                # if the answer has an element named "choices", then the question is multiple choice
                if question.get("answer").get("choices", None):
                    num_correct_answers = 0
                    for (lbl,ans) in question.get("answer").get("choices").items():
                        if( self.correct_answer_chars.find( ans[0] ) >= 0 ):
                            num_correct_answers += 1

                    if( num_correct_answers == 0 ):
                        print "WARNING: question "+str(qnum)+" appears to be a multiple-choice question, but correct answer was selected."
                        question.set("type", "MC")
                    elif( num_correct_answers == 1 ):
                        question.set("type","MC")
                    else:
                        question.set("type","MA")


                # if the answer has an element named "ordered", then the question is an ordering question
                if question.get("answer").get("ordered", None):
                  question.set("type", "ORD")


            # the answer is a bool, so the question is True/False
            if isBool( question.get("answer", None) ):
                question.set("type", "TF")



    def build_MC_tokens(self, q):
        entry = []
        entry.append( "MC" )
        entry.append( q.get("text") ) 
        lbls = sorted( q.get("answer").get("choices").leafList() )
        if self.randomize_answers:
            random.shuffle(lbls)
        for lbl in lbls:
            answer = q.get("answer").get("choices").get(lbl)
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
        entry.append( q.get("text") ) 
        # lists are stored in the tree keyed on the array index, which is a string.
        # so, we need to make sure and sort them to get the correct order
        lbls = sorted( q.get("answer").get("ordered").leafList() )
        for lbl in lbls:
            entry.append( q.get("answer").get("ordered").get(lbl) )

        return entry

    def build_NUM_tokens(self, q):
        entry = []
        entry.append( "NUM" )
        entry.append( q.get("text") )
        entry.append( '{:.2E}'.format(float(q.get("answer").get("value") ) ) ) 

        tol = q.get("answer").get("uncertainty", "1%")

        if isinstance(tol, str):
          if tol.find("%") >= 0:
            tol = float(tol.replace("%",""))/100.
            tol = tol*float(q.get("answer").get("value"))
          else:
            tol = float(tol)


        tol = abs(tol)
        entry.append( '{:.2E}'.format( tol ) )

        return entry

    def build_TF_tokens(self, q):
        entry = []
        entry.append( "TF" )
        entry.append( q.get("text") ) 
        if q.get("answer"):
            entry.append( "true" )
        else:
            entry.append( "false" )

        return entry



    def write_questions(self, filename=None):
        if not filename:
            filename = "/dev/stdout"
        with open(filename, 'w') as f:
            branches = self.quiz_tree("questions").branchList()
            branches.sort(key=float)
            for i in branches:
                if self.quiz_tree("questions").get(i).get("enabled", None):
                    if not toBool( self.quiz_tree("questions").get(i).get("enabled") ):
                        continue

                qnum = int(i) + 1
                question = self.quiz_tree("questions").get(i)
                builder = getattr(self, "build_"+question.get("type")+"_tokens")
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



