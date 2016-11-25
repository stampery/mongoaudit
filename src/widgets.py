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
