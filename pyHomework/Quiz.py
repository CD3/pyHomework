from string import Template
import StringIO, json
import re, os, yaml
import collections
import sys
import cerberus
import dpath
from mako.template import Template

class LatexLabels(dict):
    def get_newlabel_tokens( self, s ):
      '''Finds and returns newlabel tokens in a string'''

      tokens = []
      i = 0
      
      # looking for \newlabel{some_text}{{data1}{data2}} in the aux file
      tag = r'\newlabel{'
      i = s.find( tag, i+1 )
      while i > -1:  # continue while we have more \newlabel commands 

        # find the key/value pair for the \newlabel command
        j = 0
        token = []
        for k in range(2): # there are two sets of {} that we want to retrieve
          # find first '{'
          while s[i+j] != '{':
            j = j + 1

          # now find the matching '}', taking into account that there may be nested pairs
          start = i+j
          j = j+1
          count = 1
          while count > 0:
            if s[i+j] == '{':
              count = count + 1
            if s[i+j] == '}':
              count = count - 1
            j = j + 1

          end = i+j

          # append the text, removing the outer brackets
          token.append( s[start+1:end-1] )

        tokens.append( token )

        i = s.find( tag, i+1 )

      return tokens

    def get_tag( self, s ):

      j = 0
      # find first '{'
      while s[j] != '{':
        j = j + 1

      # now find the matching '}', taking into account that there may be nested pairs
      start = j
      j = j+1
      count = 1
      while count > 0:
        if s[j] == '{':
          count = count + 1
        if s[j] == '}':
          count = count - 1
        j = j + 1

      end = j

      # return the text, removing the outer brackets
      return s[start+1:end-1]



    def parse(self,filename):
        with open(filename) as file:
            data = file.read()
        
        newlabel_tokens = self.get_newlabel_tokens( data )
        rr = re.compile("\\\\bgroup\s*([0-9a-zA-Z]+)\s*\\\\egroup")
        for t in newlabel_tokens:
            label = t[0]
            tag   = self.get_tag( t[1] )
            mm = rr.findall(tag)
            tag = ''.join(mm)
            tag = tag.strip()

            key = label
            self[key] = tag


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
                
                aux_file =  os.path.join( os.path.dirname(filename) if filename else ".", self.quiz_data['latex']['aux']  )
                self.latex_labels.parse( aux_file )
        
        variables = self.quiz_data.get('vars', dict() )

        self.quiz_data = yaml.load( Template( yaml.dump( self.quiz_data ), strict_undefined=True ).render( vars = Namespace( 'vars', variables), lbls = Namespace('lbls', **self.latex_labels) ) )

        self.detect_question_types()


    def override(self, overrides = {} ):
      # if overrides is a list, it means that we have a list of 'key = val' strings that we need to parse
      # first and pass to ourself.
      if isinstance( overrides, list ):
        tmp = dict()
        for line in overrides:
          key,val = re.split( "\s*=\s*", line )
          val = eval(val)  # val is a string, which is not what we want
          tmp[key] = val

        return self.override( tmp )


      for key,val in overrides.items():
        print "Overriding '%s' with '%s'. Was '%s'" % (key,val, dpath.util.search( self.config, key ))
        dpath.util.new( self.config, key, val )

    def detect_question_types(self):
      for i in xrange(len(self.quiz_data["questions"])):
            question = self.quiz_data["questions"][i]

            # if the question has an answer that is a subtree, we need to figure out what kind of question it is
            if isinstance( question.get("answer", None), dict ):

                # if the answer has an element named "value", then the question is numerical
                if 'value' in question.get("answer"):
                    question["type"] = "NUM"

                # if the answer has an element named "choices", then the question is multiple choice
                if "choices" in question.get("answer"):
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
title : Quiz
configuration:
  make_key : True
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
