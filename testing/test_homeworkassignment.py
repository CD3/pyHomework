from pyHomework.HomeworkAssignment import *
from pyHomework.Emitter import *
import pytest

def Close( a, b, tol = 0.001 ):
    if isinstance(a,int):
        a = float(a)
    if isinstance(b,int):
        b = float(b)
    return (a - b)**2 / (a**2 + b**2) < 4*tol*tol

needsporting = pytest.mark.skipif(True, reason="Need to port to new Answer/Question/Quiz classes")

def test_interface():
  ass = HomeworkAssignment()

  ass.config('title', value='Example Homework Set')

  ass.add_paragraph("Work these problems and...")

  ass.add_question()
  ass.add_text("Q1")
  
  ass.last_question.add_part()
  ass.last_question.last_part.add_text("Q1a")

  ass.last_question.last_part.add_part()
  ass.last_question.last_part.last_part.add_text("Q1aa")

  p = Paragraph()
  p.add_text(r'This is a paragraph.')
  p.add_text(r'You can put whatever you like in here, including math:')
  p.add_text(r'$$ x = y + 2$$')
  ass.add_paragraph( p )



  ass.add_question()
  ass.add_text("Q2")

  ass.last_question.add_part()
  ass.last_question.last_part.add_text("Q2a")

  ass.last_question.add_part()
  ass.last_question.last_part.add_text("Q2b")

  ass.add_paragraph( r'a paragraph' )
  ass.add_space('1in')

  ass.add_question()
  ass.add_text("Q3")

  ass.last_question.add_part()
  ass.last_question.last_part.add_text("Q3a")

  ass.last_question.add_part()
  ass.last_question.last_part.add_text("Q3b")


  f = Figure()
  f.set_filename('test1.png')
  f.add_caption('This is a figure.')
  f.add_label('fig-')
  f.add_label('example1')
  f.add_option('width=2in')
  f.add_option('angle=90')
  ass.add_figure( f )

  f = Figure()
  f.set_filename('test2.png')
  f.add_caption('This is another figure.')
  f.add_caption(r'Refer to Figure \ref{fig-example1}.', prepend=True)
  f.add_label('fig-')
  f.add_label('example2')
  f.add_option('height=3in')
  ass.add_figure( f )



  ass.write( '/dev/stdout' )
  # ass.write( 'test.pdf' )

def test_quiz():
  ass = HomeworkAssignment()


  ass.add_question()
  ass.add_text("Question \#1")
  ref1 = ass.get_last_ref()
  
  ass.add_part()
  ass.add_text("Question \#1, Part a")
  ref1a = ass.get_last_ref()

  ass.add_part()
  ass.add_text("Question \#1, Part b")


  ass.add_question()
  ass.add_text("Question \#2")
  
  ass.add_part()
  ass.add_text("Question \#2, Part a")

  ass.add_part()
  ass.add_text("Question \#2, Part b")
  ref2b = ass.get_last_ref()


  ass.add_question()
  ass.add_text(r"Question \#3 references \ref{%s}, \ref{%s}, \ref{%s}." % (ref1,ref1a,ref2b) )

  ass.add_quiz_question()
  ass.quiz_add_text("What is the answer?")
  Answer = Q_(123456789,'N')
  ass.quiz_set_answer( NumericalAnswer( Answer ) )


  ass.add_part()
  ass.add_text(r"Question \#3, Part b, also references \ref{${r1}}, \ref{${r1a}}, \ref{${r2b}}.")
  ass.format_text( r1=ref1, formatter='template' )
  ass.format_text( r1a=ref1a, r2b=ref2b, formatter='template' )

  ass.add_quiz_question()
  ass.quiz_add_text("What is the answer?")
  Answer = UQ_(123456789,40,'dimensionless')
  ass.quiz_set_answer( NumericalAnswer( Answer ) )

  ass.build_PDF('test.pdf')
  ass.write_quiz('test-quiz.txt')

