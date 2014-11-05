#! /usr/bin/env python

from Utils import *
import sys, os, re, random
import math
import yaml #, wheezy.template, asteval
import collections

import sys
sys.path.append("../externals/pyoptiontree")
import pyoptiontree


yaml.Resolver.add_path_resolver( u'tag:yaml.org,20002:float', re.compile(""))

testing = 1

class Flattener:
    def __init__( self, ns = "", delim=".", allow_empty_ns=False, allow_leading_delim=False ):
        self.ns = ns
        self.delim = delim
        self.allow_empty_ns = allow_empty_ns
        self.allow_leading_delim = allow_leading_delim

    def __call__( self, obj ):
        return Flattener.flatten( obj, ns=self.ns, delim=self.delim, allow_empty_ns=self.allow_empty_ns, allow_leading_delim=self.allow_leading_delim )

    def clean_key( self, key ):
        if not self.allow_leading_delim:
            key = key.lstrip(self.delim)

        if not self.allow_empty_ns:
            clean_key = key.replace( self.delim+self.delim, self.delim )
            while clean_key != key:
                key = clean_key
                clean_key = key.replace( self.delim+self.delim, self.delim )
        return key

    def get_absolute_key( self, key ):
        keys = list()
        for key in key.split(self.delim):
            if key == '..':
                keys.pop()
                continue

            if key != '.':
                keys.append( key )

        return self.construct_key( keys )


    def get_parent_key( self, key ):
        return self.construct_key( key.split(self.delim)[:-1] )


    def construct_key( self, keys ):
        if type(keys) == list:
            return self.delim.join(keys)

        return keys

    @staticmethod
    def flatten( obj, ns="", delim=".", allow_empty_ns=False, allow_leading_delim=False ):
        '''
        Flattens a nested object into a single dictionary. Keys for the resultant dictionary are created
        by concatenating all keys required to access the element5 from the top.

        dict and list ojbects are flattened. all other objects are left as is.
        '''

        ret  = dict()
        if type(obj) == dict:
            for k in obj.keys():
                nns = ns + delim + k
                ret.update( Flattener.flatten( obj[k], ns=nns, delim=delim, allow_empty_ns=allow_empty_ns, allow_leading_delim=allow_leading_delim ) )
            return ret
            
        if type(obj) == list:
            for i in range(len(obj)):
                nns = ns + delim + str(i)
                ret.update( Flattener.flatten( obj[i], ns=nns, delim=delim, allow_empty_ns=allow_empty_ns, allow_leading_delim=allow_leading_delim ) )
            return ret

        f = Flattener( ns, delim, allow_empty_ns, allow_leading_delim )
        ns = f.clean_key( ns )

        ret[ns] = obj
        
        return ret


class BbQuiz:
    def __init__(self):
        self.quiz_data = None
        self.quiz_namespace = None
        self.correct_answer_chars = "*^!@"
        self.randomize_answers = True

        

    def load(self, obj):
        if isinstance( obj, str ):
            if os.path.isfile( obj ):
                with open(obj) as f:
                    self.quiz_data = yaml.load( f )

                    print self.quiz_data
                    tmp = ""
                    for (key,val) in Flattener.flatten(self.quiz_data, "", "/").items():
                        if isinstance(val,str):
                            print float(val)
                            val = "'"+val+"'"
                        tmp += str(key)+"="+str(val)+"\n"
                    self.quiz_tree = pyoptiontree.PyOptionTree()
                    self.quiz_tree.addString( tmp )

                    print self.quiz_tree
            else:
                raise IOError( "argument %s does not seem to be a file" % arg )


        if isinstance( obj, dict ):
            self.quiz_data = obj

        self.namespace = { 'global_vars' : self.quiz_data.get('vars',{} ) }
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



