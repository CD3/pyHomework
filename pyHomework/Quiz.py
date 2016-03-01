from .Question import *
from .Answer import *
from .Emitter import *
from .File import *
from .Utils import *
import dpath.util, contextlib, urlparse, os

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
  def _add_file(self,v,name=None):
    if not isinstance(v, File):
      v = File(v)

    name = name or v.filename
    self._files[name] = v
  
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

