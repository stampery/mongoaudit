# -*- coding: utf-8 -*-

import urwid
from testers import *

div = urwid.Divider()
hr = urwid.AttrMap(urwid.Divider('_'), 'hr')

def pad(w, left=2, right=2):
  return urwid.Padding(w, left=left, right=right)

class TextButton(urwid.Button):
  """
  Args:
    label (str): label for the text button
    on_press (function): callback
    user_data(): user_data for on_press
    align (str): (default right)
  """
  def __init__(self, label, on_press=None, user_data=None, align='right'):
    super(TextButton, self).__init__(label, on_press=on_press, user_data=user_data)
    self._label.align = align
    cols = urwid.Columns([self._label])
    super(urwid.Button, self).__init__(cols)

class Card(urwid.WidgetWrap):
  """
  Args:
    content (urwid.Widget):
    header (urwid.Widget):
    footer (urwid.Widget):
  """
  def __init__(self, content, header=None, footer=None):
    wlist = []
    if header:
      wlist.append(header)
    wlist.extend([div, pad(content)])
    if footer:
      wlist.extend([hr, div, pad(footer)])
    wlist.append(div)
    card = urwid.AttrMap(urwid.Pile(wlist), 'card')
    urwid.WidgetWrap.__init__(self, card)

class ObjectButton(urwid.Button):
  def __init__(self, content, on_press=None, user_data=None):
    self.__super.__init__('', on_press=on_press, user_data=user_data)

    super(urwid.Button, self).__init__(content)

class ImageButton(ObjectButton):
  """
  Creates a LineBox button with an image on the left column and text on the right
  Args:
    pic (urwid.Pile): object created with picRead
    text ((palette_class, str)[]): array of string tuples
  """
  def __init__(self, pic, text):
    content = urwid.Pile([urwid.SelectableIcon(s, 0) if i == 0 else urwid.Text(s) for i, s in enumerate(text)])
    lbox = urwid.LineBox(urwid.Pile([div, urwid.Padding(urwid.Columns([(8, pic), content], 4), left=3, right=3), div]))
    self.__super.__init__(urwid.AttrMap(urwid.Pile([lbox]), 'image button', 'image button focus'))

class InputField(urwid.WidgetWrap):
  """
  Creates an input field with underline and a label
  Args:
    label (str): label for the input
    label_width (int): label width (default 15 characters)
  """
  def __init__(self, label="", label_width=15):
    self.label = label
    self.edit = urwid.Padding(urwid.Edit(), left=1, right=1)
    label = urwid.LineBox(urwid.Text(label), tlcorner=' ', tline=' ', lline=' ', trcorner=' ', blcorner=' ', rline=' ', brcorner=' ', bline=' ' )
    lbox = urwid.AttrMap(urwid.LineBox(self.edit , tlcorner=' ', tline=' ', lline=' ', trcorner=' ', blcorner=' ', rline=' ', brcorner=' ' ), 'input', 'input focus')
    cols = urwid.Columns([(label_width, label), lbox])
    urwid.WidgetWrap.__init__(self, cols)

  def get_text(self):
    """
    Returns:
      str: value of the input field
    """
    return self.edit.original_widget.get_text()[0]

  def get_label(self):
    """
    Returns:
      str: label for the input field
    """
    return self.label

class FormCard(urwid.WidgetWrap):
  """
  Args:
    content (urwid.Widget): any widget that can be piled
    field_labels (str[]): labels for the input_fields
    btn_label (str): label for the button
    cb (function): callback to invoke when the form button is pressed
    back (function): card to render when going back
  Note:
    cb must take the same amount of arguments as labels were passed and each parameter
    in the callback must be named as the label but in snake case and lower case e.g.
    'Field Name' =>  field_name
  """
  def __init__(self, content, field_labels, btn_label, cb, back=None):
    self.fields, self.cb = [], cb
    for label in field_labels:
      self.fields.append(InputField(label))
    input_fields = urwid.Pile(self.fields)
    self.error_field = urwid.Text('')
    error_row = urwid.Columns([(17, urwid.Text('')), self.error_field])
    buttons = [TextButton(btn_label, on_press=self.next)]
    if back:
        buttons.insert(0, TextButton('Back', align='left', on_press=back))
    footer = urwid.AttrMap(urwid.Columns(buttons), 'button')

    card = Card(urwid.Pile([content, input_fields, error_row]), footer=footer)
    urwid.WidgetWrap.__init__(self, card)

  def next(self, _button=None):
    self.cb(form=self, **(self.get_field_values()))


  def get_field_values(self):
    """
    Returns:
      dict: the keys are the labels of the fields in snake_case
    """
    values = dict()
    for field in self.fields:
      values[field.get_label().lower().replace(" ", "_")] = field.get_text()

    return values

  def set_error(self, msg):
    """
    Args:
      msg (str): error message
    """
    self.error_field.set_text(('error',msg))

  def keypress(self, size, key):
    if key is 'enter':
      self.next()
    else:
      return self.__super.keypress(size, key)

class TestRunner(urwid.WidgetWrap):
  """
  Run and display test
  Args:
    cred (dict(str:str)): MongoDB credentials
    tests (): test to run

  Notes:
    After the widget has been created the function run must be called
  """
  def __init__(self, cred, tests):
    self.tester = Tester(cred, tests)
    self.test_results = urwid.Pile([])
    self.end_result = urwid.Text('')
    result = urwid.Pile([self.test_results, div, self.end_result])
    urwid.WidgetWrap.__init__(self, result)

  def each(self, test):
    options = self.test_results.options()
    title = urwid.Text('[' + ['H', 'M', 'L'][test.severity] + '] ' + test.title + ':')
    result = urwid.Text(' ' + ['✘', '✔'][test.result] + ' ' + [test.no, test.yes][test.result])
    self.test_results.contents.extend([(title, options), (result, options)])

  def end(self, res):
    count = lambda acc, test: acc+1 if test.result is not None else acc
    self.end_result.set_text('Finished running ' + str(reduce(count, res.tests, 0)) + ' tests')

  def run(self):
    self.tester.run(self.each, self.end)
