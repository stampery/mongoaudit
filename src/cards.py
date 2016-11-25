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
            'START', on_press=self.choose_test), 'button')
    card = Card(text, header=pic, footer=button)
    self.app.render(card)

  def choose_test(self, button=None):
    txt = urwid.Text(
        '%s provides two distinct types of test suites covering  security in different depth. Please choose which tests you want to run:'
        % self.app.name)

    basic = ImageButton(
        picRead('../rsc/%s' % 'bars_min.bmp'),
        [('textbold', 'Basic'),
         ('text', 'Analize server perimeter security. (Does not require valid credentials)')])
    exhaustive = ImageButton(
        picRead('../rsc/%s' % 'bars_max.bmp'),
        [('textbold', 'Exhaustive'),
         ('text', 'Connect to MongoDB server and analize security from inside. (Requires valid credentials)')])
    content = urwid.Pile([txt, div, basic, exhaustive])
    urwid.connect_signal(basic, 'click', self.basic_test)
    urwid.connect_signal(exhaustive, 'click', self.basic_test)
    card = Card(content)
    self.app.render(card)


  def basic_test(self, button):
    test = urwid.AttrMap(urwid.Text("testing"), 'focus btn')
    self.app.render(test)
