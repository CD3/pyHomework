from pyHomework.HomeworkAssignment import *
from pyHomework.Emitter import *
import pytest
import StringIO
from string import Template

def Close( a, b, tol = 0.001 ):
    if isinstance(a,int):
        a = float(a)
    if isinstance(b,int):
        b = float(b)
    return (a - b)**2 / (a**2 + b**2) < 4*tol*tol

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



  # ass.write_file( '/dev/stdout' )
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
  ass.write_quiz_file('test-quiz.txt')

def test_with_interface_output():

  refs = {}

  ass = HomeworkAssignment()
  ass._preamble = []
  ass._header = []
  ass._packages = []
  ass.add_package('easylist', 'at')
  ass.add_preamble(r'\ListProperties(Numbers1=a,Numbers2=l,Progressive*=0.5cm,Hang=true,Space=0.2cm,Space*=0.2cm)')
  
  with ass._add_question() as q:
    q.add_text('q1')
    refs['q1'] = id(q)
    assert ass.refstack[-1] == refs['q1']

  with ass._add_question() as q:
    q.add_text('q2')
    refs['q2'] = id(q)
    assert ass.refstack[-1] == refs['q2']

    with q._add_part() as p:
      p.add_text('q2a')
      refs['q2a'] = id(p)
      assert ass.refstack[-1] == refs['q2a']

    assert ass.refstack[-1] == refs['q2']

  with ass._add_question() as q:
    q.add_text('q3')
    refs['q3'] = id(q)
    assert ass.refstack[-1] == refs['q3']

    with ass.quiz._add_question() as qq:
      assert ass.refstack[-1] == refs['q3']
      qq.add_text('q3_q1')
      with qq._set_answer( MultipleChoiceAnswer() ) as a:
        a.add_choices('''
          a
          *b
        ''')
    with ass.quiz._add_question() as qq:
      assert ass.refstack[-1] == refs['q3']
      qq.add_text('q3_q2')
      with qq._set_answer( MultipleChoiceAnswer() ) as a:
        a.add_choices('''
          *c
          d
        ''')

    with q._add_part() as p:
      p.add_text('q3a')
      refs['q3a'] = id(p)
      assert ass.refstack[-1] == refs['q3a']

      with ass.quiz._add_question() as qq:
        assert ass.refstack[-1] == refs['q3a']
        qq.add_text('q3a_q1')
        with qq._set_answer( NumericalAnswer() ) as a:
          a.quantity = Q_(1.3579,'m/s')

      assert ass.refstack[-1] == refs['q3a']

    assert ass.refstack[-1] == refs['q3']

  with ass._add_question() as q:
    q.add_text('q4')
    refs['q4'] = id(q)
    assert ass.refstack[-1] == refs['q4']

  strm = StringIO.StringIO()
  ass.write(strm)

  assert strm.getvalue() == Template( r'''
\documentclass[letterpaper,10pt]{article}


\usepackage[,at]{ easylist }

\ListProperties(Numbers1=a,Numbers2=l,Progressive*=0.5cm,Hang=true,Space=0.2cm,Space*=0.2cm)


\usepackage{fancyhdr}
\setlength{\headheight}{0.5in}
\pagestyle{fancyplain}
\fancyhead[L]{  }
\fancyhead[C]{  }
\fancyhead[R]{  }
\fancyfoot[L]{  }
\fancyfoot[C]{ \thepage }
\fancyfoot[R]{ powered by \LaTeX }
\renewcommand{\headrulewidth}{0pt}

\title{ UNKNOWN }
\author{  }
\date{  }

\begin{document}
\maketitle

\begin{easylist}
@ \label{$q1}q1
@ \label{$q2}q2
@@ \label{$q2a}q2a
@ \label{$q3}q3
@@ \label{$q3a}q3a
@ \label{$q4}q4
\end{easylist}



\clearpage


\end{document}
'''.lstrip()).substitute(**refs)
  

  strm = StringIO.StringIO()
  ass.build_PDF('tmp.pdf')
  ass.write_quiz(strm)

  assert strm.getvalue() == Template('''
MC\tFor problem #3: q3_q1\ta\tincorrect\tb\tcorrect
MC\tFor problem #3: q3_q2\tc\tcorrect\td\tincorrect
NUM\tFor problem #3a: q3a_q1 Give your answer in meter / second.\t1.36E+00\t1.36E-02
'''.strip()).substitute(**refs)

# NUM\tFor problem #4: q4_q1 Give your answer in meter / second ** 2.\t1.36E+00\t5.79E-02


def test_legacy_interface_ouput():

  refs = {}

  ass = HomeworkAssignment()
  ass._preamble = []
  ass._header = []
  ass._packages = []
  ass.add_package('easylist', 'at')
  ass.add_preamble(r'\ListProperties(Numbers1=a,Numbers2=l,Progressive*=0.5cm,Hang=true,Space=0.2cm,Space*=0.2cm)')
  
  ass.add_question()
  ass.add_text('q1')
  refs['q1'] = id(ass.last_question_or_part)
  ass.add_question()
  ass.add_text('q2')
  refs['q2'] = id(ass.last_question_or_part)
  ass.add_part()
  ass.add_text('q2a')
  refs['q2a'] = id(ass.last_question_or_part)
  ass.add_question()
  ass.add_text('q3')
  refs['q3'] = id(ass.last_question_or_part)

  ass.add_quiz_question()
  ass.quiz_add_text('q3_q1')
  a = MultipleChoiceAnswer()
  a.add_choices('''
    a
    *b
    ''')
  ass.quiz_set_answer(a)

  ass.add_quiz_question()
  ass.quiz_add_text('q3_q2')
  a = MultipleChoiceAnswer()
  a.add_choices('''
    *c
    d
    ''')
  ass.quiz_set_answer(a)

  ass.add_part()
  ass.add_text('q3a')
  refs['q3a'] = id(ass.last_question_or_part)

  ass.add_quiz_question()
  ass.quiz_add_text('q3a_q1')
  ass.quiz_set_answer(NumericalAnswer(Q_(1.3579,'m/s')))


  ass.add_question()
  ass.add_text('q4')
  refs['q4'] = id(ass.last_question_or_part)

  ass.add_quiz_question()
  ass.quiz_add_text('q4_q1')
  ass.quiz_set_answer(NumericalAnswer(UQ_(1.3579,0.0579,'m/s^2')))





  strm = StringIO.StringIO()
  ass.write(strm)

  assert strm.getvalue() == Template( r'''
\documentclass[letterpaper,10pt]{article}


\usepackage[,at]{ easylist }

\ListProperties(Numbers1=a,Numbers2=l,Progressive*=0.5cm,Hang=true,Space=0.2cm,Space*=0.2cm)


\usepackage{fancyhdr}
\setlength{\headheight}{0.5in}
\pagestyle{fancyplain}
\fancyhead[L]{  }
\fancyhead[C]{  }
\fancyhead[R]{  }
\fancyfoot[L]{  }
\fancyfoot[C]{ \thepage }
\fancyfoot[R]{ powered by \LaTeX }
\renewcommand{\headrulewidth}{0pt}

\title{ UNKNOWN }
\author{  }
\date{  }

\begin{document}
\maketitle

\begin{easylist}
@ \label{$q1}q1
@ \label{$q2}q2
@@ \label{$q2a}q2a
@ \label{$q3}q3
@@ \label{$q3a}q3a
@ \label{$q4}q4
\end{easylist}



\clearpage


\end{document}
'''.lstrip()).substitute(**refs)
  

  strm = StringIO.StringIO()
  ass.build_PDF('tmp.pdf')
  ass.write_quiz(strm)

  assert strm.getvalue() == Template('''
MC\tFor problem #3: q3_q1\ta\tincorrect\tb\tcorrect
MC\tFor problem #3: q3_q2\tc\tcorrect\td\tincorrect
NUM\tFor problem #3a: q3a_q1 Give your answer in meter / second.\t1.36E+00\t1.36E-02
NUM\tFor problem #4: q4_q1 Give your answer in meter / second ** 2.\t1.36E+00\t5.79E-02
'''.strip()).substitute(**refs)
