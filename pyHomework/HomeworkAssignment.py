#! /usr/bin/env python

from .Quiz import *
from pyErrorProp import *

# ELEMENT CLASSES

class Figure(object):
  def __init__(self):
    self.filename = ""
    self.label = ""
    self.caption  = ""
    self.options = ""

class Paragraph(object):
  def __init__(self, text = ""):
    self.text = text

  def add_text(self, text):
    self.text += text + " "



# ANSWER CLASSES


# ASSIGNMENT CLASSES

class HomeworkAssignment(Quiz):

  def __init__(self):
    super( HomeworkAssignment,self ).__init__()
    self._config = { 'title' : "UNKNOWN"
                   , 'LH' : ""
                   , 'CH' : ""
                   , 'RH' : ""
                   , 'LF' : ""
                   , 'CF' : r"\thepage"
                   , 'RF' : r"powered by \LaTeX"
                   }

    self.quizzes = []
    self.figures = []

    self.latex_template= r'''
\documentclass[letterpaper,10pt]{article}
\usepackage{amsmath}
\usepackage{amsfonts}
\usepackage{amssymb}
\usepackage{graphicx}
\usepackage{siunitx}
\usepackage{fancyhdr}
\usepackage[ampersand]{easylist}
\ListProperties(Numbers1=a,Numbers2=l,Progressive*=0.5cm,Hang=true,Space=0.2cm,Space*=0.2cm)
\usepackage{hyperref}
\usepackage[left=1in,right=1in,top=1in,bottom=1in]{geometry}

\sisetup{per-mode=symbol}
\DeclareSIUnit \mile {mi}
\DeclareSIUnit \inch {in}
\DeclareSIUnit \foot {ft}
\DeclareSIUnit \yard {yd}
\DeclareSIUnit \acre {acre}
\DeclareSIUnit \lightyear {ly}
\DeclareSIUnit \parcec {pc}
\DeclareSIUnit \teaspoon {tsp.}
\DeclareSIUnit \tablespoon {tbsp.}
\DeclareSIUnit \gallon {gal}
\DeclareSIUnit \fluidounce{fl oz}
\DeclareSIUnit \ounce{oz}
\DeclareSIUnit \pound{lb}
\DeclareSIUnit \hour{hr}


\setlength{\headheight}{0.5in}
\pagestyle{fancyplain}
\fancyhead[L]{${config['LH']}}
\fancyhead[C]{${config['CH']}}
\fancyhead[R]{${config['RH']}}
\fancyfoot[L]{${config['LF']}}
\fancyfoot[C]{${config['CF']}}
\fancyfoot[R]{${config['RF']}}
\renewcommand{\headrulewidth}{0pt}

\setlength{\parindent}{0cm}

\title{${config['title']}}
\author{}
\date{}

%for line in config['preamble']:
${line}
%endfor

\begin{document}
\maketitle

%for item in config['stack']:
%if config['isQuestion']( item ):
\begin{minipage}{\linewidth}
  \begin{easylist}
  & ${'*' if item.starred else ''} \label{${item.label}} ${item.text}
  %for p in item.parts:
    && ${'*' if p.starred else ''} \label{${p.label}} ${p.text}
  %endfor
  \end{easylist}
\end{minipage}
%endif
%if config['isFigure']( item ):
\begin{figure}
\includegraphics[${item.options}]{${item.filename}}
\caption{ \label{${item.label}} ${item.caption}}
\end{figure}
%endif
%if config['isParagraph']( item ):

${item.text}

%endif
%endfor

\clearpage

%if config.get('make_key',False):
\textbf{Answers:} \\\

%for item in config['stack']:
%if config['isQuestion']( item ):
%if not item.answer is None:
  \ref{${item.label}} ${str(item.answer)} \\\
%endif
%for p in item.parts:
%if not p.answer is None:
  \ref{${p.label}} ${str(p.answer)} \\\
%endif
%endfor
%endif
%endfor
%endif

\end{document}
'''


  # def write_latex(self, stream=None):
    # if stream is None:
        # stream = "/dev/stdout"

    # if isinstance(stream,(str,unicode)):
      # basename = os.path.splitext( os.path.basename(stream))[0]
      # self.config['latex_aux'] = basename+'.aux'
      # with open(stream, 'w') as f:
        # self.write_latex( f )
      # return

    # stream.write( self.template_engine.render( config=self.config ) )

  # def write_quiz(self, stream="quiz.yaml"):
    # if stream is None:
        # stream = "/dev/stdout"

    # if isinstance(stream,(str,unicode)):
      # with open(stream, 'w') as f:
        # self.write_quiz( f )
      # return

    # # this will write a yaml file that can be processed by BbQuiz
    # tree = {'questions' : [] }
    # for item in self.stack:
      # if self.config['isQuizQuestion'](item):
        # tree['questions'].append( item.dict() )

    # if not self.config['latex_aux'] is None:
      # tree.update({ 'latex' : {'aux' : self.config['latex_aux']}})
    
    # if not self.config['quiz_config'] is None:
      # tree.update( {'configuration' : self.config['quiz_config'] } )

    # stream.write( yaml.dump(tree, default_flow_style=False) )

  # def build_PDF( self, basename="main"):
    # basename = os.path.splitext(basename)[0]
    # scratch = tempfile.mkdtemp()

    # self.write_latex(os.path.join(scratch,basename+".tex") )

    # # copy dependencies
    # for item in self.config['extra_files']:
      # fr  = item
      # to  = os.path.join(scratch, os.path.basename( item ))
      # print "Copying %s to %s" % (fr,to)
      # shutil.copy( fr, to )


    # p = subprocess.Popen(shlex.split( 'latexmk -interaction=nonstopmode -f -pdf '+basename), cwd=scratch, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # stdout,stderr = pHomeworkAssignment .communicate()
    # ret = p.returncode # if ret != 0:
      # print "ERROR: LaTeX code failed to compile. Dumping output"
      # print "vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv"
      # print stderr
      # print stdout
      # print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"

    # for ext in ("pdf", "aux", "tex"):
      # filename = "%s.%s"%(basename,ext)
      # shutil.copy( os.path.join(scratch,filename), filename)

  # def build_quiz(self, basename="quiz"):
    # basename = os.path.splitext(basename)[0]

    # self.write_quiz(basename+".yaml")

    # with open("/dev/stdout",'w') as FNULL: # ret = subprocess.call(shlex.split( 'BbQuiz.py '+basename+".yaml"), stdout=sys.stdout, stderr=subprocess.STDOUT)

  def add_paragraph(self,para):
    self.stack.append( para )

  def add_preamble(self,line):
    self.preamble.append( line )

  def add_part(self):
    pass

  def add_figure(self,filename=""):
    self.stack.append( Figure() )
    self.get_last_figure().filename = filename

    self.add_extra_file( os.path.join(self.config['image_dir'],filename) )

  def figure_set_data(self,data,text=""):
    f = self.get_last_figure()
    if f:
      setattr( f, data, text )

  def add_extra_file(self,filename):
    self.config['extra_files'].append( filename )


