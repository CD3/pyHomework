#! /usr/bin/env python

from pyHomework.Utils import *
import sys, os, re, random
import yaml
from dpath import util
import urlparse

class BbQuiz(Quiz):
    def build_MC_tokens(self, q):
        entry = []
        entry.append( "MC" )
        entry.append( q.get("text") ) 
        choices = q.get("answer").get("choices")
        if self.config['randomize']['answers']:
            random.shuffle(choices)
        for answer in choices:
            if( self.config['special_chars']['correct_answer'].find( answer[0] ) >= 0 ):
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
        questions = self.quiz_data.get("questions")
        if self.config['randomize']['questions']:
          random.shuffle(questions)
        for question in questions:
          if question.get("enabled", True):
            builder = getattr(self, "build_"+question.get("type")+"_tokens")
            q = builder(question)

            if question.get("image",None):
              link = self.push_image( question.get("image"), self.config['remote'] )
              # need to add the link to the question text, which is at q[1].
              q[1] = "To answer this question, view the picture at %s by copying the link into your browser IN A NEW TAB (DO NOT USE THIS TAB). %s" %(link, q[1])

            f.write("\t".join(q)+"\n")

    def push_image(self, image_filename, remote_config):
        data = dict()

        if 'copy_root' in remote_config:
          url = urlparse.urlparse( os.path.join( remote_config['copy_root'], remote_config['image_dir'] ) )
        else:
          return None

        if url.scheme == 'ssh':

          data['file']   = image_filename
          data['netloc'] = url.netloc
          data['path']   = url.path[1:]

          cmd = 'scp "%(file)s" "%(netloc)s:%(path)s" > /dev/null' % data
          print "found file/link pair. copying file to server with '%s'." % cmd
          os.system( cmd )
        
        link = urlparse.urljoin( remote_config['web_root'], os.path.join(remote_config['image_dir'], image_filename) )
        return link



if __name__ == "__main__":

  from argparse import ArgumentParser

  manual = '''
  {prog} reads a description of a quiz stored in a YAML file and creates a txt file formatted such that they can be imported
  into Blackboard. Blackboard can import questions from text file,
  but these files must have a specific format (https://help.blackboard.com/en-us/Learn/9.1_SP_10_and_SP_11/Instructor/070_Tests_Surveys_Pools/106_Uploading_Questions#file_format),
  which is not easy to manage. YAML is a standard file format that provides a simple syntax to organize data. It is easier
  to manage quizzes stored in YAML format.

  In addition to simplifying quiz management, {prog} also has several features for simplifying quiz writing. For example, the 'tolorance' for
  numerical answers can be automatically calculated, multiple choice answers can be randomized, and so on.
  
           '''
  parser = ArgumentParser(description="A simple script for creating Blackboard quizzes from YAML files.")

  parser.add_argument("quiz_files",
                      nargs='*',
                      action="store",
                      help="The YAML quiz files." )

  parser.add_argument('-m', '--manual',
                      action="store_true",
                      help="Print manual." )

  parser.add_argument('-e', '--example',
                      action="store",
                      help="Write an example quiz file." )


  args = parser.parse_args()

  if args.manual:
    print manual.format( prog = 'BbQuiz.py' )
    sys.exit(0)

  if args.example:
    quiz = BbQuiz()
    with open( args.example, 'w' ) as f:
      f.write( quiz.dump_example() )
    sys.exit(0)

  for arg in args.quiz_files:
      quiz = BbQuiz()
      quiz.load( arg )
      quiz.write_questions(os.path.splitext(arg)[0]+".txt")



