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
