# -*- coding: utf-8 -*-

import urwid

div = urwid.Divider()
hr = urwid.AttrMap(urwid.Divider('_'), 'hr')

def pad(w, left=2, right=2):
  return urwid.Padding(w, left=left, right=right)

class TextButton(urwid.Button):
  def __init__(self, label, on_press=None, user_data=None):
    super(TextButton, self).__init__(label, on_press=on_press, user_data=user_data)
    cols = urwid.Columns([self._label])
    super(urwid.Button, self).__init__(cols)

class Card(urwid.WidgetWrap):
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
  def __init__(self, pic, text):
    content = urwid.Pile([urwid.SelectableIcon(s, 0) if i == 0 else urwid.Text(s) for i, s in enumerate(text)])
    lbox = urwid.LineBox(urwid.Pile([div, urwid.Padding(urwid.Columns([(8, pic), content], 4), left=3, right=3), div]))
    self.__super.__init__(urwid.AttrMap(urwid.Pile([lbox]), 'image btn', 'focus btn'))

class InputField(urwid.WidgetWrap):
  def __init__(self, label="", label_width=20):
    self.label = label
    self.edit = urwid.Edit()
    lbox = urwid.LineBox(self.edit , tlcorner=' ', tline=' ', lline=' ', trcorner=' ', blcorner=' ', rline=' ', brcorner=' ' )
    label = urwid.LineBox(urwid.Text(label), tlcorner=' ', tline=' ', lline=' ', trcorner=' ', blcorner=' ', rline=' ', brcorner=' ', bline=' ' )
    cols = urwid.Columns([(label_width, label), lbox])
    urwid.WidgetWrap.__init__(self, cols)

  def get_text(self):
    return self.edit.get_text()[0]

  def get_label(self):
    return self.label

class FormCard(urwid.WidgetWrap):
  """
  Args:
    content (urwid.Widget): any widget that can be piled
    field_labels (str[]): labels for the input_fields
    btn_label (str): label for the button
    cb (function): callback to invoke when the form button is pressed
  Note:
    cb must take the same amount of arguments as labels were passed and each parameter
    in the callback must be named as the label but in snake case and lower case e.g.
    'Field Name' =>  field_name
  """
  def __init__(self, content, field_labels, btn_label, cb):
    self.fields = []

    for label in field_labels:
      self.fields.append(InputField(label))

    input_fields = urwid.Pile(self.fields)

    button = urwid.AttrMap(
        TextButton(btn_label, on_press=(lambda _: cb(**(self.get_field_values())))), 'button')

    card = Card(urwid.Pile([content, input_fields, button]))
    urwid.WidgetWrap.__init__(self, card)

  def get_field_values(self):
    values = dict()
    for field in self.fields:
      values[field.get_label().lower().replace(" ", "_")] = field.get_text()

    return values
