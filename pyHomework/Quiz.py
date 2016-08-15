# local imports
from .Question import *
from .Answer import *
from .Emitter import *
from .File import *
from .Utils import *

# standard modules
import os, sys, tempfile, subprocess
import contextlib, urlparse, urllib, StringIO, base64

# non-standard modules
import dpath.util
import pyparsing as pp

try:
  sys.path.append( os.getcwd() )
  import macros
  have_user_macros = True
except:
  have_user_macros = False

class Quiz(object):
  Question = Question
  DefaultEmitter = PlainEmitter

  def __init__(self):
    self._config = {}

    self._questions = []
    self._order = []
    self._file = []


  def config(self,key,default=None,value=None):
    if isinstance(key,dict):
      for k in key:
        self.config(k, value=key[k])
    if value is None:
      try:
        return dpath.util.get(self._config,key)
      except:
        return default
    else:
      dpath.util.new(self._config,key,value)

  @property
  def questions(self):
    for i in self.order:
      yield self._questions[i]

  @property
  def order(self):
    _order = self._order

    if self.config('/randomize/questions',False):
      random.shuffle( _order )
    for i in _order:
      yield i

  @order.setter
  def order(self,v):
    self._order = v

  @property
  def last_question(self):
    if len( self._questions ) > 0:
      i = self._order[-1]
      return self._questions[i]
    else:
      return None



  @contextlib.contextmanager
  def _add_question(self,q=None):
    if not isinstance(q, Question):
      q = self.Question(q)

    yield q

    self._order.append( len(self._questions) )
    self._questions.append( q )

  def add_question(self,*args,**kwargs):
    with self._add_question(*args,**kwargs):
      pass


  @contextlib.contextmanager
  def _add_file(self,f,name=None):
    if not isinstance(f, File):
      f = File(f)

    yield f

    name = name or v.filename
    self._files[name] = f
  
  def add_file(self,*args,**kwargs):
    with self._add_file(*args,**kwargs):
      pass

  def set_file(self,*args,**kwargs):
    self._files = {}
    return self._add_file(*args,**kwargs)




  def emit(self,emitter=None):
    if emitter == None:
      emitter = self.DefaultEmitter

    if self.config('randomize/answers', False):
      for q in self._questions:
        for a in q._answers:
          a.randomize = True

    if inspect.isclass( emitter ):
      return self.emit( emitter() )

    if not emitter is None and hasattr(emitter,'__call__'):
      return emitter(self)

    raise RuntimeError("Unknown emitter type '%s' given." % emitter)

  def write(self, stream="/dev/stdout"):
    if isinstance(stream,(str,unicode)):
      with open(stream, 'w') as f:
        return self.write(f)
    
    stream.write( self.emit() )

  def load(self,spec):
    self._config.update(spec.get('configuration',{}))
    for q in spec['questions']:
      self.add_question()
      try:
        self.add_text( q['text'] )
      except:
        raise RuntimeError("No text found in question: %s" % q)

      if 'instructions' in q:
        self.add_instruction( q['instructions'] )

      self.add_answer( make_answer(q['answer']) )

  def find(self,pattern):
    '''Find and return a question matching a search string.'''
    for q in self.questions:
      if pattern in q:
        return q

    return None


def passthrough_fn( fn_name ):
  def func(self, *args, **kwargs):
    return getattr(self.last_question,fn_name)(*args,**kwargs)
  setattr(Quiz,fn_name, func)
passthroughs = ['add_text'
               ,'add_instruction'
               ,'add_answer'
               ,'set_text'
               ,'set_instruction'
               ,'set_answer'
               ,'clear_text'
               ,'clear_instruction'
               ,'clear_answer'
               ]
for p in passthroughs:
  passthrough_fn(p)


# we want to support uploading files to a remote URL and referencing them in
# a question.
class BbQuizQuestion(Question):
  link_instruction_template = 'Before answering this question, view this link ({view_url:s}) in a NEW TAB.'
  def __init__(self,*args,**kwargs):
    super(BbQuizQuestion,self).__init__(*args,**kwargs)
    self._files = {}

  @contextlib.contextmanager
  def _add_file(self,f,name=None):
    if not isinstance(f, File):
      f = File(f)

    yield f

    name = name or f.filename
    self._files[name] = f
    self.add_pre_instruction( self.link_instruction_template, prepend=True )
  
  def add_file(self,*args,**kwargs):
    with self._add_file(*args,**kwargs):
      pass




class BbQuiz(Quiz):
    DefaultEmitter = BbEmitter
    Question = BbQuizQuestion
    def __init__(self,*args,**kwargs):
      super(BbQuiz,self).__init__(*args,**kwargs)
      self._config = { 'files' :
                         { 'view_url'  : 'http://example.com/files/{tag:s}/{filename:s}'
                         , 'push_url'  : 'ssh://example.com/files/{tag:s}/{filename:s}'
                         , 'local_url' : '/path/to/the/files/{filename:s}'
                         , 'tag' : 'default'
                         , 'docopy' : True
                         }
                    , 'randomize' :
                        { 'questions' : False
                        , 'answers'   : False
                        }
                    }

      self.Question._files_config = self._config['files']

    def push_files(self):
      for q in self._questions:
        for k in q._files:
          f = q._files[k]
          fname = f.filename
          bname = os.path.basename(f.filename)
          context = { 'filename' : f.filename
                    , 'abspath' : os.path.abspath( f.filename )
                    , 'basename' : os.path.basename( f.filename )
                    , 'tag' : self.config('/files/tag', 'default')
                    }
          push_url = format_text( self.config('files/push_url'), 'format', **context )
          url = urlparse.urlparse( push_url )
          if url.scheme == 'ssh':
            remote_file = url.path[1:] # don't want the leading '/'
            local_file  = format_text( self.config('/files/local_url'), 'format', **context )
            cmd = 'scp "{lfile:s}" "{netloc:s}:{rfile:s}"'
            cmd = format_text( cmd, 'format', netloc=url.netloc, rfile=remote_file, lfile=local_file )
            print "found file/link pair. copying file to server with '%s'." % cmd
            if self.config('/files/docopy', False):
              # create the remote directory in case it does not exist
              os.system( format_text( 'ssh {netloc:s} "mkdir -p {rpath}"', 'format', netloc=url.netloc, rpath=os.path.dirname(remote_file) ) )
              os.system( cmd )
        
    def write(self, stream="/dev/stddev"):
      if isinstance(stream,(str,unicode)):
        with open(stream, 'w') as f:
          return self.write(f)
      

      sstream = StringIO.StringIO()
      super(BbQuiz,self).write(sstream)

      text = sstream.getvalue()

      # replace macro shorthands first
      #    $...$ --> \math{...}
      #    *...* --> \emph{...}
      #    **...** --> \textbf{...}
      for qc,rep in [ (r'$', r'\math{%s}')
                    , (r'**', r'\textbf{%s}')
                    , (r'*', r'\emph{%s}')
                    ]:
        text = pp.QuotedString(quoteChar=qc).setParseAction(lambda toks: rep%toks[0]).transformString( text )



      # Replace macros.
      command = pp.Word(pp.alphas)
      options = pp.QuotedString( quoteChar='[', endQuoteChar=']')
      options = pp.originalTextFor( pp.nestedExpr( '[', ']' ) )
      arguments = pp.originalTextFor( pp.nestedExpr( '{', '}' ) )

      macro = pp.Combine( pp.Literal("\\") + command("command") + pp.Optional(options)("options") + pp.ZeroOrMore(arguments)("arguments") )
      macro.setParseAction( self.expand_macro )

      # transform string until all macros have been expanded
      while True:
        newtext = macro.transformString( text )
        if newtext == text:
          break
        text = newtext



      # try to catch some syntax errors that will cause Bb to choke

      # 1. MC or MA questions don't have a "correct" answer
      for line in text.split('\n'):
        if line.startswith('MC') or line.startswith('MA'):
          if not re.search("\tcorrect", line):
            print "WARNING: A multiple choice/answer question does not have a correct answer. Blackboard will not parse this."
            print "\t",line[3:50],'...'
            print

      stream.write( text )





    def make_img_html( self, stream, fmt=None, opts="" ):
      '''Read image from stream or file and return html code with the image embedded.'''
      if isinstance(stream, (str,unicode)):
        afn = os.path.join( os.getcwd(), stream )
        afn = os.path.normpath(afn)

        if not os.path.isfile( afn ):
          raise RuntimeError("ERROR: could not find image file '%s'." % afn )
        with open(afn,'r') as f:
          trash,ext = os.path.splitext( afn )
          return self.make_img_html(f,ext,opts)

      code  = base64.b64encode(stream.read())
      text  = r'''<img src="data:image/{fmt};base64,{code} {opts}>'''.format(fmt=fmt,code=code,opts=opts)
      return text

    def expand_macro(self,toks):

      command = str(toks.command)
      options = str(toks.options).lstrip('[').rstrip(']')
      arguments = [str(x).lstrip('{').rstrip('}') for x in toks.arguments]


      # replacement = getattr(self,"macro_"+command)(arguments,options)
      replacement = None
      if have_user_macros and hasattr(macros,command):
          replacement = getattr(macros,command)(self,arguments,options)
      elif hasattr(self,"macro_"+command):
          replacement = getattr(self,"macro_"+command)(arguments,options)

      if replacement:
        replacement = re.sub( "\n", " ", replacement )

      return replacement


    macro_emph   = lambda self,args,opts :  "<em>"+args[0]+"</em>"
    macro_textbf = lambda self,args,opts :  "<strong>"+args[0]+"</strong>"

    def macro_includegraphics(self,args,opts):

      fn = args[0]
      text = self.make_img_html( args[0], opts='alt="{fn}"'.format(fn=fn) )
      return text

    def macro_math(self,args,opts=None):
      # send the LaTeX snippet to www.codecogs.com
      # and get an image of the equation
      # to embed in an img tag.

      # replace white space with &space;
      latex = re.sub('\s+','&space;',args[0])

      # get the image
      fmt = 'png'
      url = "https://latex.codecogs.com/{fmt}.latex?{latex}".format(fmt=fmt,latex=latex)

      # we can either use the url as the image src, or download the image, encode it and embed it
      # as the source. We are going to embed the image so that we don't hav to worry about the link
      # breaking in the future. but, in case you are interested, this is what we would do if we
      # just wanted to link
      # text = r'''<img src="{url}" title="{latex}" alt="ERROR: Could not render math."/>'''.format(url=url,latex=latex)
      # return text

      resource = urllib.urlopen(url)
      with tempfile.TemporaryFile() as fp:
        while True:
          txt = resource.read()
          if len(txt) == 0:
            break
          fp.write(txt)
        fp.seek(0)
        text = self.make_img_html( fp, fmt, opts='alt="ERROR: Could not render math"' )

      return text


    def macro_shell(self,args,opts):
      '''Run shell command and return output.'''
      with tempfile.TemporaryFile() as fp:
        cmd = ';'.join(args)
        subprocess.call( cmd, shell=True, stdout=fp )
        fp.seek(0)
        stdout = fp.read()

      return stdout


    @contextlib.contextmanager
    def _add_question(self,*args,**kwargs):
      with super(BbQuiz,self)._add_question(*args,**kwargs) as qq:
        yield qq
        for k in qq._files:
          filename = qq._files[k].filename
          context = { 'filename' : filename
                    , 'abspath' : os.path.abspath( filename )
                    , 'basename' : os.path.basename( filename )
                    , 'tag' : self.config('/files/tag', 'default')
                    }
          view_url = format_text( self.config('files/view_url'), 'format', **context )
          qq.format_pre_instructions( formatter = 'format', view_url = view_url )

