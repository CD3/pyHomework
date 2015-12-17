
class File(object):
  def __init__(self,filename = ""):
    self._filename = filename

  @property
  def filename(self):
    return self._filename
