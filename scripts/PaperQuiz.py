#! /usr/bin/env python

from pyHomework.Utils import *
import sys, os, re, random
import yaml
import dpath.util
import subprocess, tempfile, shutil, shlex
import pyPdf
from mako.template import Template



latex_template= r'''
<%!
    import random
    import collections

    answers = collections.OrderedDict()
%>

<%
    def mca( text ):
      if isAns( text ):
        text = text[1:]
      return text

    def isAns( text ):
      return special_chars['correct_answer'].find( text[0] ) >= 0
%>



\documentclass[letterpaper,10pt]{article}
\usepackage{amsmath}
\usepackage{amsfonts}
\usepackage{amssymb}
\usepackage{graphicx}
\usepackage{siunitx}
\usepackage{paralist}
\usepackage[left=0.5in,right=0.5in,top=0.5in,bottom=0.5in]{geometry}


\begin{document}
\begin{center}
{\Large ${title}}
\end{center}

%if not instructions is UNDEFINED:
Special Instructions:
\begin{itemize}
  %for instruction in instructions:
    \item ${instruction}
  %endfor
\end{itemize}
\vspace{10pt}
Questions:
\vspace{10pt}
%endif

\begin{compactenum} <% i = 0 %>
%for question in questions:
<%
  i += 1
  qlbl = '\label{%d}' % i
  qref = qlbl.replace("label", "ref")
  answers[qref] = []
%>\begin{minipage}{\linewidth}
    \item ${qlbl} ${question['text']}
    %if question['type'] == "MC" or question['type'] == "MA":
    \begin{compactenum} <% j = 0 %>
        %for choice in question['answer']['choices']:
        <% 
          j += 1
          plbl = '\label{%d%d}' % (i,j)
          pref = plbl.replace("label", "ref")
          if isAns( choice ):
            answers[qref].append( pref )
        %>\item ${plbl} ${choice|mca}
        %endfor
    \end{compactenum}
    %endif
    %if question['type'] == "TF":

        True \hskip 1cm False
    %endif
    <%
      if question['type'] == "NUM":
        answers[qref].append( str( question['answer']['value'] ) )
        answers[qref][-1] +=  str( question['answer'].get('unit', "") )

      if question['type'] == "TF":
        answers[qref].append( "True" if question['answer'] else "False" )
    %>
    \end{minipage}

    \vspace{10pt}

%endfor
\end{compactenum}

%if make_key:
\clearpage
Key - Quiz Answers:
\begin{itemize}
  %for k in answers:
      \item ${k}.
    %for v in answers[k]:
            ${v} 
    %endfor
  %endfor

\end{itemize}
%endif

\end{document}
'''


class PaperQuiz(Quiz):
    def __init__(self):
        super( PaperQuiz, self).__init__()
        self.template_engine = Template(latex_template, strict_undefined=False )
        self.answers = []


        self.config['make_key'] = False
        self.quiz_data['title'] = "Quiz"



    def write_questions(self, filename=None):

      if self.config['randomize']['questions']:
        random.shuffle(self.quiz_data['questions'])

      if self.config['randomize']['answers']:
        for q in self.quiz_data['questions']:
          if q['type'] == "MC" or q['type'] == "MA":
            random.shuffle( q['answer']['choices'] )

      if not filename:
          filename = "/dev/stdout"
      with open(filename, 'w') as f:
        render_data = dict()
        render_data.update(self.config)
        render_data.update(self.quiz_data)
        f.write( self.template_engine.render( **render_data ) )

    def compile_latex(self, filename):
        basename = os.path.splitext(arg)[0]
        pdf      = basename+".pdf"
        cwd = os.getcwd()
        temp = tempfile.mkdtemp()

        
        shutil.copy( filename, temp )
        os.chdir( temp )

        #ret = subprocess.call(shlex.split( 'pdflatex --interaction=batchmode '+basename) )
        #ret = subprocess.call(shlex.split( 'pdflatex --interaction=batchmode '+basename) )
        #ret = subprocess.call(shlex.split( 'bibtex '+basename) )
        #ret = subprocess.call(shlex.split( 'pdflatex --interaction=batchmode '+basename) )
        with open(os.devnull,'w') as FNULL:
          ret = subprocess.call(shlex.split( 'latexmk -pdf '+basename), stdout=FNULL, stderr=subprocess.STDOUT)


        shutil.copy( pdf, cwd)
        os.chdir( cwd)

    def preview_pdf(self, filename):
      with open(os.devnull,'w') as FNULL:
        viewer = args.preview_viewer
        ret = subprocess.call([viewer,filename], stdout=FNULL, stderr=subprocess.STDOUT)

    def split_quiz_and_key(self, filename):
      '''Splits a PDF containing into the quiz and a separate key'''

      FirstKeyPage = -1
      pdfDoc = pyPdf.PdfFileReader(open(filename, "rb"))
      for i in xrange(pdfDoc.getNumPages()):
          content = ""
          content += pdfDoc.getPage(i).extractText() + "\n"
          content = content.encode('ascii', 'ignore')
          if content.find( "Key-QuizAnswers:" ) > -1:
            FirstKeyPage = i
            break

      if FirstKeyPage > -1:

        # write the quiz first write the key
        output = pyPdf.PdfFileWriter()
        ofilename = filename.replace(".pdf", "-Key.pdf")
        for i in xrange(FirstKeyPage, pdfDoc.getNumPages() ):
          output.addPage(pdfDoc.getPage(i))
        with open( ofilename, 'wb' ) as f:
          output.write(f)

        # now write the quiz.
        output = pyPdf.PdfFileWriter()
        ofilename = filename.replace(".pdf", "-Quiz.pdf")
        for i in xrange(0, FirstKeyPage):
          output.addPage(pdfDoc.getPage(i))
        with open( ofilename, 'wb' ) as f:
          output.write(f)


        # overwrite the original quiz
        shutil.move( ofilename, filename)



if __name__ == "__main__":
  from argparse import ArgumentParser

  parser = ArgumentParser(description="A simple Python script for creating paper quizzes from a YAML configuration file.")

  parser.add_argument("quiz_files",
                      action="store",
                      nargs='*',
                      help="Quiz YAML files." )

  parser.add_argument("-p", "--preview",
                      action='store_true',
                      help="Preview the generated PDF after it is created. In other words... open it" )

  parser.add_argument("-P", "--preview-viewer",
                      action='store',
                      default='evince',
                      help="Preview the generated PDF after it is created. In other words... open it" )

  parser.add_argument('-e', '--example',
                      action="store",
                      help="Write an example quiz file." )

  parser.add_argument('-c', '--config-var',
                      action="append",
                      help="Override parameter in configuration file." )

  parser.add_argument("-l", "--list-config",
                      action='store_true',
                      help="Show all configuration options." )

  args = parser.parse_args()

  if args.example:
    quiz = PaperQuiz()
    with open( args.example, 'w' ) as f:
      f.write( quiz.dump_example() )
    sys.exit(0)

  for arg in args.quiz_files:
    basename = os.path.splitext(arg)[0]
    quiz = PaperQuiz()
    quiz.load( arg )
    for v in args.config_var:
      key,val = v.split('=')
      print "Overriding '%s' with '%s'. Was '%s'" % (key,val, dpath.util.search( quiz.config, key ))
      dpath.util.new( quiz.config, key, val )
    if args.list_config:
      print quiz.config

    quiz.write_questions(    basename+".tex" )
    quiz.compile_latex(      basename+".tex" )
    quiz.split_quiz_and_key( basename+".pdf" )
    if args.preview:
      quiz.preview_pdf(      basename+".pdf" )


