# -*- coding: utf-8 -*-

import urwid
from picmagic import read as picRead
from widgets import *


class Cards(object):

  def __init__(self, app):
    self.app = app

  def welcome(self):
    pic = picRead('../rsc/welcome.bmp', align='right')
    text = urwid.Text((
        'text',
        '%s is a CLI tool for auditing MongoDB servers, detecting poor security settings and performing automated penetration testing.'
        % self.app.name))
    button = urwid.AttrMap(
        TextButton(
            'START', on_press=self.chooseTest), 'button')
    card = Card(text, header=pic, footer=button)
    self.app.render(card)

  def chooseTest(self, button=None):
    txt = urwid.Text(
      '%s provides two distinct types of test suites covering  security in different depth. Please choose which tests you want to run:'
      % self.app.name)

    basic = self.genTestButton(
        'bars_min.bmp', [('textbold', 'Basic'),
                         ('text', 'Analize server perimeter security. (Does not require valid credentials)')])
    exhaustive = self.genTestButton(
        'bars_max.bmp', [('textbold', 'Exhaustive'),
                         ('text', 'Connect to MongoDB server and analize security from inside. (Requires valid credentials)')])
    content = urwid.Pile([txt, div, basic, exhaustive])
    card = Card(content)
    self.app.render(card)

  def genTestButton(self, image, text):
    pic = picRead('../rsc/%s' % image)
    content = urwid.Pile(map(lambda s: urwid.Text(s), text))
    lbox = urwid.LineBox(urwid.Pile([div,urwid.Padding(urwid.Columns([(8,pic), content],4), left=3, right=3), div]))
    # lbox = urwid.LineBox(urwid.Columns([(8,pic), content],3))
    return ButtonObject(lbox)
