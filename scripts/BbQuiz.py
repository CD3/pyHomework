#! /usr/bin/env python
"""
  BbQuiz: generate Blackboard quizzes from YAML spec files.

  Usage:
    BbQuiz.py [-l] [-c STR]... [-o FILE]<quiz-file> ...
    BbQuiz.py -m
    BbQuiz.py -e FILE

  Options:
    -e FILE, --example FILE                     write an example quiz file and exit.
    -c STR, --config-var STR, --override STR    specify a configuration override.
    -l, --list-config                           list configuration options (for debug).
    -o, --output FILE                           write output to FILE. default is to replace extention of spec file with .txt


"""

from pyHomework.Quiz import *
import sys, os, re, random
import yaml
import dpath.util
import urlparse

class BbQuiz(Quiz):
    def __init__(self,*args,**kwargs):
      super(BbQuiz,self).__init__(*args,**kwargs)
      self._config = { 'files' :
                         { 'view_url'  : 'http://example.com/files/{filename:s}'
                         , 'push_url'  : 'ssh://example.com/files/{filename:s}'
                         , 'local_url' : '/path/to/the/files/{filename:s}'
                         }
                    , 'randomize' :
                        { 'questions' : False
                        , 'answers'   : False
                        }
                    }

    def write_quiz(self, filename="/dev/stdout"):
      with open(filename, 'w') as f:
        f.write( self.emit('bb') )

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
        print "Overriding '%s' with '%s'. Was '%s'" % (key,val, dpath.util.search( self._config, key ))
        self.config(key,value=val)

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
        
        # the link that points to the image may not be the same as the url we copied it too, so we want to construct the
        # correct link and return it.
        link = urlparse.urljoin( remote_config['web_root'], os.path.join(remote_config['image_dir'], os.path.basename(image_filename) ) )
        return link
    def dump_example(self):
      text = '''
title : Quiz
configuration:
  make_key : True
  randomize:
    questions: True
    answers: False
  files:
    view_url  : http://example.com/files/{filename:s}
    push_url  : ssh://example.com/files/{filename:s}
    local_url : /path/to/the/files/{filename:s}

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



if __name__ == "__main__":

  from docopt import docopt
  arguments = docopt(__doc__, version='0.1')

  if not arguments['--example'] is None:
    quiz = BbQuizSpec()
    with open( arguments['--example'], 'w' ) as f:
      f.write( quiz.dump_example() )
    sys.exit(0)

  for arg in arguments['<quiz-file>']:
    quiz = BbQuiz()

    with open(arg,'r') as f:
      quiz.load( yaml.load(f) )
    quiz.override( arguments['--override'] )

    if arguments['--list-config']:
      print quiz.config

    outfile = os.path.splitext(arg)[0]+".txt"
    if arguments['--output'] is not None:
      outfile = arguments['--output']
    quiz.write_quiz(outfile)



