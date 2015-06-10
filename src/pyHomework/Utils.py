#! /usr/bin/env python

from string import Template
import StringIO, json
import re, os, yaml
import collections
import sys
from mako.template import Template
import cerberus

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




class LatexLabels(dict):
    def parse(self,filename):
        with open(filename) as file:
            data = file.read()
        
        r  = re.compile("\\\\newlabel\{([^\}]+)\}\{\{([^\}]+)\}\{([^\}]+)\}\}")
        rr = re.compile("\\\\bgroup\s*([0-9a-zA-Z]+)\s*\\\\egroup")
        for match in r.findall( data ):
            (label,tag,page) = match
            match = rr.search(tag)
            if match:
                tag = match.group(1)

            tag = tag.strip()

            key = label
            self[key] = tag

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

def isBool(v):
  return str(v).lower() in ('true', 'yes','false','no','0','1')

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

def dict2list( d ):
    l = [None]*len( d )
    for k in d:
      # we can't just append here because we won't get the index numbers in order
      l[int(k)] = d[k]
    return l

class Quiz(object):

    class QuizValidator(cerberus.Validator):
      def __init__(self, *args, **kwargs):
        quiz_schema = '''
        questions:
          required : True
          type : list
          schema :
            type : dict
            allow_unknown : True
            schema:
              image: {type: string}
              type:  {type: string}
              text:  {type: string, required: False }
              answer:
                anyof:
                  - type: dict
                    schema :
                      value: {type : [number, string], required: False}
                      uncertainty: {type : [number, string] }
                  - type: dict
                    schema:
                      choices: {type : list, required: False}
                  - type: dict
                    schema:
                      ordered: { type : list, required: False}
                  - type: boolean
        configuration:
          type: dict
          schema :
            randomize :
              type : dict
              schema :
                questions : {type : boolean}
                answers   : {type : boolean}
            special_chars : 
              type : dict
              schema :
                correct_answer : {type : string}
        '''
        if 'schema' not in kwargs:
          kwargs['schema'] = yaml.load(quiz_schema)
        super(Quiz.QuizValidator,self).__init__(*args, **kwargs)




    def __init__(self):
        self.quiz_data = dict()
        self.latex_labels = LatexLabels()
        self.config = { 'special_chars' : { 'correct_answer' : "*^!@" }
                      , 'randomize' : { 'answers' : True
                                      , 'questions' : False }
                      }
        


    def validate(self):
      v = Quiz.QuizValidator( )
      if not v.validate( self.quiz_data ):
        print v.document
        raise cerberus.ValidationError( yaml.dump( v.errors, default_flow_style=False) )
      else:
        return True




    def load(self, filename = None, text = None, quiz_data = None):
        class Namespace(dict):

          def __init__(self, name, *args, **kwargs):
            self.name = name
            dict.__init__(self, *args, **kwargs )

          def __getattr__(self,key):
            return dict.get(self,key,"${%s.%s}" % (self.name, key))

        self.filename = "unknown"
        if not filename is None:
          self.filename = filename
          with open( filename, 'r' ) as f:
            text = f.read()

        if quiz_data is None:
          # want to run the input file through Mako first, so the user
          # can use some sweet template magic
          self.quiz_data.update( yaml.load( Template(text, strict_undefined=True).render( vars = Namespace('vars'), lbls = Namespace("lbls") ) ) )

        else:
          self.quiz_data = quiz_data

        # update configuration with config in entry in config file
        self.config.update( self.quiz_data.get('configuration', dict() ) )

        # run the data tree through Mako to do variable replacement, including latex refernce/label replacement
        # this is pretty slick, we do the following:
        # 1. build a dictionary of variables from the latex aux file and the 'vars' entry of the yaml file
        # 2. dump the dict to a yaml string.
        # 3. pass this string to the Mako template class.
        # 4. render the template using the variables we git in part 1
        # 5. parse the new yaml to a dict tree

        # load latex keys if available
        if 'latex' in self.quiz_data:
            if 'aux' in self.quiz_data['latex']:
                aux_file =  os.path.join( os.path.dirname(obj), self.quiz_data['latex']['aux']  )
                self.latex_labels.parse( aux_file )
        
        variables = self.quiz_data.get('vars', dict() )

        self.quiz_data = yaml.load( Template( yaml.dump( self.quiz_data ), strict_undefined=True ).render( vars = Namespace( 'vars', variables), lbls = Namespace('lbls', **self.latex_labels) ) )

        self.detect_question_types()

    def detect_question_types(self):
      for i in xrange(len(self.quiz_data["questions"])):
            question = self.quiz_data["questions"][i]

            # if the question has an answer that is a subtree, we need to figure out what kind of question it is
            if isinstance( question.get("answer", None), dict ):

                # if the answer has an element named "value", then the question is numerical
                if question.get("answer").get("value", None):
                    question["type"] = "NUM"

                # if the answer has an element named "choices", then the question is multiple choice
                if question.get("answer").get("choices", None):
                  # we need to see how many correct answers there are...
                  num_correct_answers = 0
                  for ans in question.get("answer").get("choices"):
                    if( self.config['special_chars']['correct_answer'].find( ans[0] ) >= 0 ):
                      num_correct_answers += 1

                  # if there weren't any correct answers, there was probably an error
                  if( num_correct_answers == 0 ):
                    print "WARNING: question %d in file '%s' appears to be a multiple-choice question, but no correct answer was selected." % (i+1,self.filename)
                    question["type"] = "MC"
                  # if there was only one answer, this is a multiple choic
                  elif( num_correct_answers == 1 ):
                    question["type"] = "MC"
                  # otherwise, it is a multiple-answer
                  else:
                    question["type"] = "MA"


                # if the answer has an element named "ordered", then the question is an ordering question
                if question.get("answer").get("ordered", None):
                  question["type"] = "ORD"


            # the answer is a bool, so the question is True/False
            if isBool( question.get("answer", None) ):
                question["type"] = "TF"


