
import sys, os
moddir = os.path.join( os.path.dirname( __file__ ), '../src' )
sys.path = [moddir] + sys.path

from pyHomework.Utils import Quiz

def test_simple():
  quiz_text= '''
configuration:
  randomize:
    questions: True
    answers: False
  special_chars:
    correct_answer : '*'

questions:
  - 
    text: "What is the correct answer?"
    answer:
      choices:
      - '*this is the correct answer'
      - 'this is not the correct answer'
      - 'this is also not the correct answer'

  - 
    text: "What answers are correct?"
    answer:
      choices:
      - '*this is a correct answer'
      - 'this is not a correct answer'
      - '*this is also a correct answer'

  - 
    text: "Put these items in the correct order"
    answer:
      ordered :
      - 'first'
      - 'second'
      - 'third'
  - 
    text: "What is the correct numer?"
    answer:
      value : 7

  - 
    text: "What is the correct numer, plus or minus 20%?"
    answer:
      value : 7
      uncertainty: 20%
  - 
    text: "Is the answer True?"
    answer: True
  - 
    text: "Can you see the picture?"
    image: './picture.png'
    answer:
      choices:
        - '*yes'
        - 'no'
  # vvv not valid vvv
  #- 
    #text: "Can you see the picture?"
    #answer :
      #unknown : this is not a valid q type
  #- 
    #text: "Can you see the picture?"
  #- 
    #text: 10
  '''

  q = Quiz()
  q.load( text = quiz_text )
  q.validate()
