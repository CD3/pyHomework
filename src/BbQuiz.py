#! /usr/bin/env python

from Utils import *
import sys, os, re, random
import math
import yaml #, wheezy.template, asteval
import collections
from dpath import util
import pprint
import urlparse

import sys
sys.path.append("../externals/pyoptiontree")
import pyoptiontree


testing = 0



class BbQuiz(Quiz):

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
                if question.get("graphic",None):
                    self.push_graphic( question.get("graphic") )

    def push_graphic(self, element):

        data = dict()

        data['file'] = element.get("file", None)
        link = urlparse.urlparse( element.get("link", "") )

        data['user'] = 'cdclark'
        data['host'] = link.netloc
        data['path'] = link.path.replace('/~cclark','./public_html')

        cmd = 'scp "%(file)s" "%(user)s@%(host)s:%(path)s" > /dev/null' % data

        print "found file/link pair. copying file to server with '%s'." % cmd
        os.system( cmd )
        





if __name__ == "__main__":
    for arg in sys.argv[1:]:
        quiz = BbQuiz()
        quiz.load( arg )
        quiz.write_questions(os.path.splitext(arg)[0]+".Bb")


if testing:
    print EvalTemplate("this is interpolated once ${x}").substitute( EvalTemplateDict({'x' : 10, 'y' : "${x}"}))
    print EvalTemplate("this is interpolated once ${y}").substitute( EvalTemplateDict({'x' : 10, 'y' : "${x}"}))



