# -*- coding: utf-8 -*-

import urwid
from picmagic import read as picRead
from widgets import *

class Cards(object):

  def __init__(self, app):
    self.app = app

  def welcome(self):
    pic = picRead('../rsc/welcome.bmp', align='right')
    text = urwid.Text(('text', '%s is a CLI tool for auditing MongoDB servers, detecting poor security settings and performing automated penetration testing.' % self.app.name))
    button = urwid.AttrMap(TextButton('START', on_press=self.chooseTest), 'button')
    card = Card(text, header=pic, footer=button)
    self.app.render(card)

  def chooseTest(self, button=None):
    content = urwid.Pile([
      urwid.Text('%s provides two distinct types of test suites covering  security in different depth. Please choose which tests you want to run:' % self.app.name)
    ])
    card = Card(content)
    self.app.render(card)
