from os import path
from pydm import Display


class MyDisplay(Display):
  def __init__(self, parent=None, args=None, macros=None):
    super(MyDisplay, self).__init__(parent=parent, args=args, macros=macros)

  def ui_filename(self):
    return 'main.ui'

  def ui_filepath(self):
    return path.join(path.dirname(path.realpath(__file__)), self.ui_filename())