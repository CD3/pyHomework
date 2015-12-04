

class Quiz(object):
  class Question(object):
    def __init__(self):
      self.text = []
      self.instructions = []
      self.image = None

    def add_text(self, text):
      self.text.append(text)

    def add_instruction(self, text):
      self.instructions.append(text)

    def add_image(self, name):
      self.image = name


  def __init__(self):
    self.questions = []
    pass


  def get_last_question( self ):
    if len( self.questions ) > 0:
      return self.questions
    else:
      return None



