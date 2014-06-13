#! /usr/bin/env python

import sys, os, re, random
from string import Template
import math
import yaml, wheezy.template
import __builtin__

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

class BbQuiz:
    def __init__(self):
        self.quiz_data = None
        self.correct_answer_chars = "*^!@"
        self.randomize_answers = True

        

    def load(self, obj):
        if isinstance( obj, str ):
            if os.path.isfile( obj ):
                with open(obj) as f:
                    self.quiz_data = yaml.load( f )
            else:
                raise IOError( "argument %s does not seem to be a file" % arg )

        if isinstance( obj, dict ):
            self.quiz_data = obj

        self.interpolate()
        self.detect_question_types()

    def detect_question_types(self):
        for question in self.quiz_data["questions"]:

            if isinstance( question.get("answer", None), dict):
                if "value" in question.get("answer", {}):
                    question["type"] = "NUM"

                if "a" in question.get("answer", {}):
                    num = 0
                    for lbl in question.get("answer", {}):
                        if( self.correct_answer_chars.find( question["answer"][lbl][0] ) >= 0 ):
                            num += 1
                    if( num == 0 ):
                        pass
                    elif( num == 1 ):
                        question["type"] = "MC"
                    else:
                        question["type"] = "MA"

            if isinstance( question.get("answer", None), list ):
                question["type"] = "ORD"

            if isinstance( question.get("answer", None), bool ):
                question["type"] = "TF"

    def interpolate(self):
        global_vars = self.quiz_data.get("vars", {})
        for question in self.quiz_data["questions"]:
            local_vars = question.get("vars",{})
            subs = InterpDict( local_vars )
            subs.update( { 'global' : global_vars}  )
            subs.update( math.__dict__ )
            question["text"] = Template(question["text"]).substitute(subs)

            if isinstance( question.get("answer", None), dict):
                for lbl in question.get("answer", {} ):
                    question["answer"][lbl] = Template(str(question["answer"][lbl])).substitute(subs)
            if isinstance( question.get("answer", None), list ):
                for i in range(len(question.get("answer", [] ) ) ):
                    question["answer"][i] = Template(str(question["answer"][i])).substitute(subs)



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
        tol = q["answer"]["uncertainty"]
        if isinstance(tol, str) and tol.find("%") >= 0:
            tol = float(tol.replace("%",""))/100.
            tol = tol*float(q["answer"]["value"])

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
        with open(filename, 'a') as f:
            for question in self.quiz_data["questions"]:
                builder = getattr(self, "build_"+question["type"]+"_tokens")
                q = builder(question)
                f.write("\t".join(q)+"\n")




if __name__ == "__main__":
    for arg in sys.argv[1:]:
        quiz = BbQuiz()
        quiz.load( arg )
        quiz.write_questions(os.path.splitext(arg)[0]+".Bb")


print "this is a(n) %(foo)s expression" % {'foo':"static", 'bar':"foober"}
print "this is a(n) %(foo)s expression" % InterpDict( {'foo':"static", 'bar':"foober"} )
print "this is a(n) %(1+2)s expression" % InterpDict( {'foo':"static", 'bar':"foober"} )
print "this is a(n) %(foo+bar)s expression" % InterpDict( {'foo':"static", 'bar':"foober"} )
print "this is a(n) %(nested['foo'])s expression" % InterpDict( {'foo':"static", 'bar':"foober", 'nested' :{ 'foo' : 'nested_static' } } )
subs = InterpDict( {'x':10, 'foo':'static', 'bar':'foober', 'nested' :{ 'foo' : 'nested_static' }} )
subs.update( math.__dict__ )
print "this is a(n) calculated %(sin(x))s expression" % subs



