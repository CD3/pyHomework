from .Question import *
from .Answer import *
import dpath.util

class Quiz(object):
  Question = Question
  DefaultEmitter = None

  def __init__(self):
    self._config = {}

    self._questions = []
    self._order = []
    self._file = []


  def config(self,key,default=None,value=None):
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

  @property
  def question(self):
    return self.last_question


  def add_question(self,text=None):
    self._order.append( len(self._questions) )
    self._questions.append( Question(text) )

  def add_file(self,filename,name=None):
    name = name or filename
    self._files[name] = filename

  def set_file(self,*args,**kwargs):
    self._files = {}
    self.add_file(*args,**kwargs)

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

  def write(self, filename="/dev/stdout"):
    with open(filename, 'w') as f:
      f.write( self.emit() )

  def load(self,spec):
    self._config = spec.get('configuration',{})
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
