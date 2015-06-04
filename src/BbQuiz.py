#! /usr/bin/env python

from pyHomework.Utils import *
import sys, os, re, random
import math
import yaml
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
        choices = q.get("answer").get("choices")
        if self.randomize_answers:
            random.shuffle(choices)
        for answer in choices:
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
        for answer in q.get("answer").get("ordered"):
            entry.append( answer )

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


    def write_questions(self, filename="/dev/stdout"):
      with open(filename, 'w') as f:
        for question in self.quiz_data.get("questions", None):
          if question.get("enabled", True):
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
        quiz.write_questions(os.path.splitext(arg)[0]+".txt")


if testing:
    print EvalTemplate("this is interpolated once ${x}").substitute( EvalTemplateDict({'x' : 10, 'y' : "${x}"}))
    print EvalTemplate("this is interpolated once ${y}").substitute( EvalTemplateDict({'x' : 10, 'y' : "${x}"}))



