#! /usr/bin/env python

from string import Template
import StringIO, json
import re, os, yaml
import collections
import sys
from mako.template import Template
import cerberus

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
              text:  {type: string, required: True }
              answer:
                anyof:
                  - type: dict
                    schema :
                      value: {type : [number, string], required: True }
                      uncertainty: {type : [number, string] }
                  - type: dict
                    schema:
                      choices: {type : list, required: True }
                  - type: dict
                    schema:
                      ordered: { type : list, required: True }
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

    def dump_example(self):
      text = '''
configuration:
  randomize:
    questions: True
    answers: False
  special_chars:
    correct_answer : '*^'
  remote:
    web_root: 'http://scatcat.fhsu.edu/~user/'
    copy_root: 'ssh://user@scatcat.fhsu.edu/~/public_html'
    image_dir : 'images'

questions:
  - 
    text: "(Multiple Choice) What is the correct answer?"
    answer:
      choices:
      - '*this is the correct answer'
      - 'this is not the correct answer'
      - 'this is also not the correct answer'

  - 
    text: "(Multiple Answers) What answers are correct?"
    answer:
      choices:
      - '*this is a correct answer'
      - 'this is not a correct answer'
      - '*this is also a correct answer'

  - 
    text: "(Ordered) Put these items in the correct order"
    answer:
      ordered :
      - 'first'
      - 'second'
      - 'third'
  - 
    text: "(Numerical Answer) What is the correct number?"
    answer:
      value : 7

  - 
    text: "(Numerical Answer) What is the correct number, plus or minus 20%?"
    answer:
      value : 7
      uncertainty: 20%
  - 
    text: "(True/False) Is the answer True?"
    answer: True
  - 
    text: "(Image Example) Can you see the picture?"
    image: './picture.png'
    answer:
      choices:
        - '*yes'
        - 'no'

      '''

      return text
